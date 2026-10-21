# ai_lock

Smartest lock in the world! Now powered with AI and Arduino!

## Resources

- https://ctf.harrisongreen.me/2020/midnightsunctf/avr/
- https://blog.attify.com/flare-4-ctf-write-part-4/

## Writeup

In order to solve the challenge, figure out the employee pin through initial check.

Then discover the hidden commands `PREDICT`/`PARAMSET` to manipulate the simple neuron.

Set the model to generate the required key (which can be discovered by reversing the first check near congrats).

Use [exploit.txt](exploit.txt) to set the commands and get the flag!
