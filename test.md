{{#extend 'base.html'}}
  {{#finding 'ballot.sol:18-23' 'Low: First finding'}}
    Test low severity finding in constructor
  {{/finding}}
  {{#finding 'ballot.sol:18-23' 'Medium: Second finding'}}
    Test medium severity finding in constructor
  {{/finding}}
  {{#finding 'ballot.sol:25-30' 'Low: Third finding'}}
    Test low severity finding in giveRightToVote combined with earlier findings
  {{/finding}}
  {{#finding 'ballot.sol:48-55' 'Low: Fourth finding'}}
    Test low severity finding in vote on its own
  {{/finding}}
{{/extend}}
