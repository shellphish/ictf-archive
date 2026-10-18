The challenge is basically about figuring out the strategy of the bot, which can be summarized as: 

1. Before the human player wins the first set: the bot just does random throws.
2. After first win of human player and before the human player wins 5 sets: the bot repeats the last throw of human player.
3. After the human player wins 5 sets: the bot remembers all the past sets. It simply believes that the human player will decide which throw to go with based on the throws made by both parties in this round. Therefore it goes back in history and finds the last time that the exact throws were made, and decides a winning throw based on what happened in history immediately after that matched round. If there's no matching set in the past, the bot gets puzzled and just repeats the last throw.

This is a bit mouthful LOL but the participants can (hopefully) figure these out quickly with the mumbles of the bot. The behavior of the bot is mostly deterministic, so easy to go step by step.

Also as the bot's strategy is quite static, the participants can build an agent that picks up how the bot behaves and outsmarts it.
