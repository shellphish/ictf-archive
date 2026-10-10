# Street Fighter CTF Challenge

A CTF challenge where participants must create intelligent agents to fight in Street Fight-style combat. 
Your agent must complete training and defeat AI opponents to win the flag!

## Challenge Overview

In this challenge, participants must create an agent that will fight on their behalf in a turn-based combat system. The agent must:

1. **Train** with Master Jee-Oh Vhun-Ee to learn strategic information about itself and the opponent
3. **Fight** in the arena using turn-based combat mechanics
4. **Win** by defeating the opponent to reveal the flag

Each combatant/opponent can perform five attacks: "punch", "kick", "sweep", "elbow", "headbutt"
Each attack has a success rate (0-1) and a damage value (1-10).
For example, a kick with success rate 0.65 and damage 7, will succeed 65% of the times, dealing a 7 in damage. 
In the remaining 35% of the cases, the kick will fail and no damage will be caused.

Each attack has a corresponding defense:
   "punch": "parry",
   "kick": "block",
   "sweep": "jump",
   "elbow": "sidestep",
   "headbutt": "brace"

Each defense has a success rate (0-1). 
For example, if an opponent has successfully performed a "punch" with damage 5, the combatant can attempt a "parry" move (say, with success rate 0.5).
If the defense is successful, then no damage is received.
Otherwise the damage is deducted from the combatant's strength.

The combatant and the opponent are given a random profile with the following characteristics:
1. The combatant's sum of damages of all attacks is 25; the opponent's is 65. Each has a random distribution across the attacks.
   For example:
   "punch": 5,
   "kick": 3,
   "sweep": 10,
   "elbow": 1,
   "headbutt": 6
2. The success rates of the attacks and defenses are random (0-1).

### Interaction with the Trainer
A combatant has to first go to the trainer (an MCP server) and call the endpoint "train".
This will return a unique random training ID.
The combatant can then call "action" passing the training ID as parameter and obtain in return a message that specifies the step in the fight (e.g., "1") and the attack (e.g., "headbutt").
The combatant can then call "reaction" again passing the training ID, the step ID (i.e., "1"), and the correct reaction (e.g., "brace").
At any time the combatant can call "status" and find out if the training has been completed ("in_progress", "success", or "failure")
After a random number (3-10) of correct interactions, the training is over, unlocking the next steps.

At that point, the combatant can call the "assessment" endpoint, passing the training ID, which will disclose the damage and success rate numbers of the combatant itself.
The combatant can also call the "opponent" endpoint, passing the training ID, which will disclose the name and description of the opponent, as well as the damage and success rate numbers of the opponent.

### Interaction with the Arena

Once the information about itself and the opponent have been gathered, the combatant can interact with the arena (an MCP server).
The combatant can start a fight using the "fight" endpoint, passing the training_id from a successful training to demonstrate readiness. The arena returns the ID of the fight.
The combatant calls "action" and "reaction" in alternation. "action" always returns the opponent's attack for the current step. "reaction" is the combatant's response (defense or counter-attack). 
When the opponent attacks and hits successfully, the combatant can defend (parry/block/jump/sidestep/brace) or counter-attack, in both cases the arena computes the success rate and determines if the attack was blocked by a defense or if the counter-attack was successful, which case the arena will make the opponent try a defense and calculate its success. 
When the opponent attacks and misses, the combatant should not defend (defense is useless since the attack missed) and instead counter-attack (punch/kick/sweep/elbow/headbutt); 
in this case, the arena chooses the corresponding defense for that attack and checks if it succeeds. 

The combatant can at any point call "status" and get the health level of itself and the opponent.
If the opponent heath get to 0, the status will also return the flag of the challenge.
If the combatant flag gets to 0 the challenge is over and "status" will return "no flag, this time"

