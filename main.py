#!/usr/bin/env python

import argparse
from collections import namedtuple
import itertools
import markdown
import os
import pybars
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments_lexer_solidity import SolidityLexer
import UserDict

parser = argparse.ArgumentParser(description='Generate and print ECDSA keypairs.')
parser.add_argument('template', metavar='TEMPLATE', type=str, help='Template file to use')

OVERLAP = 5  # Number of lines gap allowed between findings to merge them

Finding = namedtuple('Finding', ['index', 'filename', 'title', 'startline', 'endline', 'description'])
Section = namedtuple('Section', ['items', 'code', 'startline'])
FileFinding = namedtuple('FileFinding', ['filename', 'sections'])

compiler = pybars.Compiler()


def _finding(this, options, location, title):
    data = this.context.setdefault('findings', [])
    index = this.context['index'] = this.context.get('index', 0) + 1
    description = options['fn'](this)
    startline, endline = None, None
    if ':' in location:
        location, lines = location.split(':')
        startline, endline = [int(x) for x in lines.split('-')]
    data.append(Finding(index, location, title, startline, endline, description))
    return []


def buildSection(findings, code):
    code = '\n'.join(code[findings[0].startline: findings[-1].endline])
    return Section(findings, code, findings[0].startline)


def buildFileFinding(filename, sets):
    code = open(filename).read().split('\n')
    return FileFinding(filename, [buildSection(x, code) for x in sets])


def consolidateFindings(findings):
    findings = list(findings)
    findings.sort(key=lambda f: (f.filename, f.startline))
    files = []
    for filename, group in itertools.groupby(findings, key=lambda f: f.filename):
        currentSet = []
        findingSets = [currentSet]
        for finding in group:
            if len(currentSet) > 0 and currentSet[-1].endline + OVERLAP < finding.startline:
                currentSet = []
                findingSets.append(currentSet)
            currentSet.append(finding)
        files.append(buildFileFinding(filename, findingSets))
    return files


def _code(this, options):
    fileFindings = consolidateFindings(this.get('findings'))
    ret = []
    for fileFinding in fileFindings:
        ret.extend(options['fn'](pybars.Scope(fileFinding, this, this.root)))
    return ret


def _highlight(this, options, startline):
    return highlight(
        '\n'.join(options['fn'](this)),
        SolidityLexer(),
        HtmlFormatter(linenos='table', linenostart=startline))


def readFile(filename):
    data = open(filename).read().decode('utf-8')
    if filename.lower().endswith('.md'):
        data = markdown.markdown(data)
    return data


def _extend(this, options, filename):
    outer = compiler.compile(readFile(filename))
    this.context['@content'] = options['fn'](this)
    result = outer(this, helpers=helpers)
    del this.context['@content']
    return result


helpers={
    'finding': _finding,
    'code': _code,
    'highlight': _highlight,
    'extend': _extend,
}


def main(args):
    template = compiler.compile(readFile(args.template))
    outfile = os.path.splitext(args.template)[0] + '.html'
    open(outfile, 'w').write(template(
        {'css': HtmlFormatter().get_style_defs('.highlight')},
        helpers=helpers
    ))


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
