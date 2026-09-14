---
title: "How to Actually Choose the Right AI Agent"
lane: nate-herk
source_ref: "https://www.youtube.com/watch?v=6LNlCpQPYFc"
title_date:
date_published: 2026-09-12
date_captured: 2026-09-14
rights_status: "browser-exported YouTube transcript; internal analysis only; reuse and quotation not cleared"
capture_method: "in-app browser YouTube transcript export"
speaker: "Nate Herk; Mark Kashef"
host: "Nate Herk"
speaker_status: "multi-speaker transcript inferred from title/channel; not diarized"
notes: "Internal Singularity Science archive intake. Preserve transcript bulk locally; use only original synthesis, short citations, and rights-aware source attribution outside archive."
---

# How to Actually Choose the Right AI Agent

## Source Metadata

- Lane: `nate-herk`
- Source reference: https://www.youtube.com/watch?v=6LNlCpQPYFc
- Channel: Nate Herk | AI Automation
- Date published: 2026-09-12
- Date captured: 2026-09-14
- Rights status: `browser-exported YouTube transcript; internal analysis only; reuse and quotation not cleared`
- Capture method: in-app browser YouTube transcript export
- Speaker: Nate Herk; Mark Kashef
- Host: Nate Herk

## Intake Notes

Internal Singularity Science archive intake. Preserve transcript bulk locally; use only original synthesis, short citations, and rights-aware source attribution outside archive.

## Transcript
YouTube transcript
Video ID: 6LNlCpQPYFc
Language: en
Captions: auto-generated

[0:00] All right, so Marge, by the end of
[0:02] today's episode, what will everyone have
[0:04] learned from you?
[0:04] >> My goal is that by the end of this
[0:06] video, you understand that the harness
[0:08] of a model is [music] much more
[0:09] important than the model itself.
[0:10] >> It feels to me like Claude Code is like
[0:12] a wise old owl and then it feels like
[0:14] Codex is like the Rottweiler. It'll obey
[0:16] your commands and it will just keep
[0:17] going until [music] it's it's done.
[0:19] Because whenever we talk about, oh,
[0:20] Claude's better or Codex is better, you
[0:23] have this brain they're all fighting
[0:24] about, but everything around the brain
[0:26] is actually [music] what gets it to
[0:27] tick. This stuff isn't like magic at
[0:29] all. There is a whole factory of workers
[0:32] [music] that are making this model look
[0:33] way smarter than it is. My number one
[0:35] goal is to never be loyal to a provider
[0:38] only be loyal to my harness and my
[0:40] assets and I will switch the brain
[0:42] [music] interchangeably.
[0:43] >> So I think that is really important to
[0:44] be thinking you're building up your own
[0:46] IP and you need to make sure that you're
[0:48] protecting that. And I always think of
[0:49] the quote you can outsource the thinking
[0:51] [music] but you can never outsource the
[0:52] understanding. Skills and agents though
[0:54] decay incredibly fast to the point where
[0:57] Boris Churnney dropped a tweet saying
[0:59] you should [music] delete all of your
[1:01] skills every six months. All of them.
[1:04] >> Did he?
[1:04] >> Do you know why?
[1:05] >> Why did he say that?
[1:09] [music]
[1:11] >> All right. So, Mark, thank you so much
[1:13] for joining us today in person, which is
[1:15] awesome. We're in the beautiful country
[1:17] of Montenegro, which has been so much
[1:18] fun. We're here for an AI event and we
[1:20] figured why not sit down together and
[1:23] hopefully drop some sauce today. So, I'm
[1:25] super super pumped to be sitting down.
[1:26] If you guys don't know who Mark is, then
[1:28] hopefully after this video you start
[1:30] seeing his videos on your YouTube feed
[1:31] because his stuff is absolutely gold.
[1:33] I've been watching him for a while. I
[1:35] actually was watching him before I
[1:36] started making content. So, pretty cool
[1:37] moment for me to be able to sit down
[1:39] with Mr. Cashf here today. But, yeah,
[1:41] I'm super excited to dig in. been
[1:43] getting obviously tons of questions in
[1:44] the community and discussion around oh
[1:46] like we should be should we be using
[1:48] Hermes now or we've seen this local
[1:49] thing called PI and there's just so many
[1:51] tools going around and I think we want
[1:52] to make sure that what we're building at
[1:54] the end of the day is still relevant
[1:55] next year and the year after that
[1:57] because we don't know what might happen
[1:58] to cloud code next or codec so excited
[2:01] to dig in and um yeah thanks for kind of
[2:04] throwing together an excell let's let's
[2:05] start getting into it
[2:06] >> absolutely so so the first thing I want
[2:08] to do is just really lock in on this
[2:10] diagram specifically this little brain
[2:12] in a jar are here because whenever we
[2:14] talk about oh claude's better or codeex
[2:16] is better or gemini maybe one date might
[2:18] be better you have this brain they're
[2:20] all fighting about but everything around
[2:22] the brain is actually what gets it to
[2:24] tick so if we look at the different
[2:26] parts here so we have the ability to
[2:29] read we have the ability to write and
[2:30] edit files we have the ability to use
[2:33] what's called bash which basically takes
[2:35] control of your computer makes folders
[2:37] moves folders all of these things aren't
[2:39] baked into the model and you see this if
[2:42] you ever use a local model and you say
[2:44] make me a website and spin it up on my
[2:47] local computer. It can do the first part
[2:49] but it can't do the second part.
[2:50] >> It is a brain that can tell you it can
[2:52] give you this output of the HTML but it
[2:55] can't go and spin up a local server on
[2:57] your computer. It doesn't have the limbs
[2:59] for that. So the more you start thinking
[3:01] about models in the sense that they are
[3:03] the brain but everything around them
[3:04] allows them to interact and have hands
[3:06] and legs then you start to really
[3:08] separate what is the importance of the
[3:10] brain versus everything around it and
[3:12] how can you enrich everything around it
[3:14] so you're less dependent on that brain
[3:16] >> because we are at a point where many
[3:18] local models whether it's a Kimmy or
[3:20] insert name of open source model here
[3:22] >> they can do like 80% of the day-to-day
[3:25] work
[3:25] >> you might not get the same firepower as
[3:27] you would with cloud code or codeex But
[3:29] for more and more roles increasingly for
[3:32] the next year especially I see a world
[3:34] where you run 70 to 80% on local
[3:37] assuming you have the hardware and you
[3:39] bring in the geniuses for genius level
[3:40] tasks are planning.
[3:41] >> Mhm.
[3:42] >> I love that because I think when you
[3:44] start to really talk about cloud chat in
[3:47] the web
[3:48] >> versus a cloud code
[3:50] >> there is a gap there which honestly I
[3:53] wish they didn't call it cloud code.
[3:54] >> Yeah. Because the code part is all of
[3:57] these these tools that you mentioned and
[3:58] so like just to walk us through a really
[4:00] practical example. What is the
[4:02] difference between you asking claude
[4:04] chat to let's just say research
[4:06] something for you and create a PDF
[4:07] versus when you might ask cla code to do
[4:09] that exact same task?
[4:11] >> Yeah. So claude on the web versus cloud
[4:13] code on Yeah. So cloud on the web will
[4:16] have slightly different tools. So let's
[4:18] say you're using cloud chat and all it
[4:20] can really do is do the researching
[4:22] part, create the PDF part, but some
[4:24] parts in between maybe calling
[4:25] additional uh platforms or moving files
[4:28] on your computer might it might not have
[4:29] access to local files on your computer.
[4:31] It would have to do a lot of work
[4:33] assuming things in the background that
[4:35] it can't actually touch and feel and
[4:37] see.
[4:38] >> With the cloud code as a harness, it can
[4:41] not only interact with your local
[4:42] computer, it can interact with the
[4:44] cloud. So you have the best of both
[4:45] worlds. So you have one that is telling
[4:47] you hypothetically here's what we could
[4:49] do and it could can do some stuff
[4:51] increasingly it's getting better. I see
[4:53] a world where claude chat evaporates
[4:55] completely and all we have is co-work
[4:57] which is a light version of the harness
[4:59] of cloud code.
[5:00] >> So everything we will interact with will
[5:02] have a harness. It's just to what extent
[5:05] is it highly capable to do the task
[5:07] you're looking for?
[5:08] >> 100%. And what I think is so cool about
[5:10] cloud code and you know when I started
[5:12] learning about it I remember how
[5:13] intimidated I was to start learning
[5:15] about it back in maybe January of like
[5:17] this year
[5:18] >> but when I just started asking it
[5:20] questions it feels like magic because
[5:24] yes you're interacting with the same
[5:25] model you might be used to but all of
[5:26] the harness stuff really just happens
[5:28] automatically because the harness is
[5:30] essentially built to understand here are
[5:31] the tools that I have as you can see in
[5:33] this diagram which well done on this
[5:34] diagram by the way it knows what's in
[5:37] there same way like you think
[5:38] >> you need you pick up a glass of water,
[5:40] your hands and your shoulder and it just
[5:42] works together to do it for you. So, I
[5:44] think that it's really cool to see
[5:45] something like this and even though it
[5:47] might at a glance look like you might
[5:49] have to know how to do the bash or the
[5:50] read or whatever.
[5:51] >> Yeah.
[5:52] >> But the model just takes care of it.
[5:53] >> Yeah. And what I want to focus on is
[5:55] although these come out of the box,
[5:57] right, that's the whole point of the
[5:58] cloth code harness. That's what made it
[5:59] amazing is you have the read, you have
[6:01] the edit, all the stuff is done for you.
[6:03] And even with things like Pi, which is
[6:04] kind of like a very vanilla open- source
[6:06] version where you can build your own
[6:08] harness, that's all cool, but where you
[6:10] come in and where your channel has been
[6:11] really adding tons of value is what else
[6:14] can you add to this factory? So now you
[6:15] have things like Lego blocks that are
[6:17] modular and these are those skills,
[6:19] these plugins, um all of these
[6:21] additional things you can layer on. So
[6:23] then you have this ecosystem, we have
[6:25] this orchestra where you have the brain
[6:26] in the middle telling everything else
[6:28] exactly what the goal is. And depending
[6:30] on the intelligence of the model, it
[6:32] might become better at knowing ah for
[6:34] this I need some bash with a write and
[6:36] I'll need to go through what's called
[6:37] the agentic loop which is purely you ask
[6:40] thing thing gets executed result of
[6:43] thing happens the result could be an
[6:45] error it could be a success it takes
[6:47] that stimuli and it keeps going in that
[6:49] loop and its ability to keep going in
[6:51] that loop comma well is fully based on
[6:53] how sophisticated that harness is a
[6:56] better model will know how to use tools
[6:58] better. It's kind of like bringing an
[7:00] expert handy person who's worked for a
[7:03] year and studied for many ages versus
[7:07] someone who has all the battle scars,
[7:09] the really powerful types of tools and
[7:11] has a tasset knowledge of when and where
[7:13] to use them a little bit better.
[7:15] >> They'll perform infinitely more
[7:17] powerfully than the first one.
[7:19] >> So the same concept here, both are going
[7:20] to be smart. So the model itself is
[7:22] great, but if I showed you right now an
[7:23] example,
[7:24] >> can we pop over to let's say an LM
[7:26] studio? So let's pop over here.
[7:28] >> Yeah. So what is LM Studio to anyone
[7:30] that's never used it before?
[7:31] >> Yeah. So think of LM Studio as your
[7:33] ability to run chat GPT with an open-
[7:37] source model. It doesn't have a harness
[7:40] by default. So you can just interact
[7:41] with the brain, which is beautiful
[7:43] because it'll show you exactly why we
[7:45] have an issue here.
[7:46] >> Mhm.
[7:46] >> So if I go and I'm just using Quen 27B
[7:50] here. I have some more powerful models,
[7:51] but I don't want this computer to
[7:53] explode while I'm recording it.
[7:54] >> So I'm just going to say using the
[7:55] beautiful Glido.
[7:57] >> Okay. So, I want you to make a very
[7:59] basic landing page for my AI
[8:01] consultancy. I want you to call it
[8:03] prompt advisors and I want you to spin
[8:05] it up locally on my computer so I can
[8:07] host it and show the entire audience.
[8:10] Now, if I run this over, no matter how
[8:12] much time this takes, it will be able to
[8:14] tell me that it can't spin it up. The
[8:18] reason why is it does not have the limb
[8:20] of being able to interact with my
[8:21] computer to even create that server.
[8:23] >> Mhm.
[8:24] >> You get this exact same request to
[8:25] codeex or cloud code. It's not going to
[8:27] sweat even twice because it comes with
[8:29] that out of the box. So now it's going
[8:32] to create what is the HTML itself
[8:35] because all it can do is take input and
[8:38] get output. Imagine if your brain was in
[8:40] a jar. All you can get is some form of
[8:42] stimuli and release the signal of like
[8:44] what you think the answer would be. Same
[8:46] concept. So one can theoretically do the
[8:49] thing,
[8:50] >> but it can't take it from a all the way
[8:51] to the touchdown.
[8:52] >> Yeah. The whole point of the harness is
[8:54] how do we go from the output of this
[8:55] very intelligent model to some form of
[8:57] tangible output in your hands.
[8:59] >> Totally. Yeah. And I I actually remember
[9:01] hearing some stories when you know
[9:02] Claude first started to come around
[9:04] first started to come around before we
[9:06] had the harnesses and you would hear
[9:08] these stories of these companies that
[9:10] were building products because they were
[9:12] having Claude write code and then just
[9:13] copying and pasting it into whatever
[9:15] they needed to actually build the code
[9:16] and host it and all that kind of thing.
[9:18] And that just it's another one of the
[9:20] examples that goes right along with like
[9:22] this is still inherently very powerful
[9:24] but not as powerful as when you kind of
[9:26] give it the whole agentic loop that you
[9:27] talked about earlier. All right guys,
[9:29] real quick. Huge thanks to Clay for
[9:30] sponsoring this part of the video. Now,
[9:32] one of the most common questions I get
[9:33] is where to actually find leads for cold
[9:35] outreach and how to learn enough about
[9:37] these people to send them something that
[9:38] they'll actually open because a raw list
[9:40] of names doesn't tell you things like if
[9:42] they have decision-making authority and
[9:44] how to reach them or what they even care
[9:46] about. So, Clay is a data enrichment and
[9:48] orchestration platform. And it gives you
[9:50] access to over 250 data providers and AI
[9:52] research tools all in one spot. So,
[9:55] instead of asking your agent to dig up
[9:56] whatever it can find online, you can
[9:58] research a whole list at once and pull
[10:00] the right person to contact their work
[10:02] email and the size of their company. And
[10:04] if one provider comes back empty, Clay
[10:06] just moves down the list to the next one
[10:07] until it gets you a result. And what's
[10:09] really cool is the logic you build stays
[10:11] attached to your data. So the same steps
[10:13] can be run again and again on every new
[10:15] lead that you add. And you can see each
[10:17] step that it took, like which provider
[10:18] every value came from and what it cost
[10:20] you. You can build all of this from
[10:22] Cloud Code with the Clay CLI, which is
[10:24] what I'm doing right here. So try Clay
[10:26] using the link in the description, and
[10:27] you'll get 2,000 free credits. Now,
[10:29] let's get back to the video. Okay, so we
[10:31] talked about how important these pieces
[10:32] are because this is where you can really
[10:34] start to add in your own like subject
[10:35] matter expertise,
[10:36] >> which is really what helps make the
[10:37] system feel more like it's yours. And
[10:39] what's cool about this stuff is that as
[10:42] you build on like maybe these skills,
[10:43] context files, plugins, whatever it may
[10:45] be, you're not locking yourself in to
[10:47] that harness because these can be used
[10:49] across other harnesses and other models
[10:51] as well.
[10:51] >> So the question I wanted to ask you is
[10:54] as you switch through these things and
[10:55] you know your codecs can touch your
[10:57] AIOS, your second brain, whatever
[10:58] everyone's calling it these days,
[11:00] Hermes, openclaw, whatever comes next.
[11:02] How do you personally, Mark Cashup, how
[11:04] do you think about the way that you
[11:06] switch between those harnesses and like
[11:08] you know if you like codecs for certain
[11:11] tasks, Hermes for certain tasks, what
[11:12] does that look like for you?
[11:13] >> For sure. So my number one goal is to
[11:16] never be loyal to a provider to only be
[11:18] loyal to my harness and my assets and I
[11:21] will switch the brain
[11:23] >> interchangeably. I have zero loyalty to
[11:25] that.
[11:26] >> So although I use cloud code a lot, it's
[11:27] more so I'm used to it. I know the
[11:28] rhythm of it. I know what to expect.
[11:30] Mhm.
[11:30] >> But I will create all of my skills so
[11:32] they can work with any language model
[11:34] open to closed source
[11:36] >> and I will prioritize really battle
[11:38] testing it with every single thing that
[11:40] I can. So I'll try with cloud code. Then
[11:42] I have the skill I call / poly skill.
[11:44] It'll convert any skill for cloud code
[11:46] and optimize it for codeex.
[11:48] >> Okay.
[11:48] >> So I'll make sure that every skill is
[11:50] eligible for both.
[11:51] >> That both all of the different models
[11:53] know exactly where to find the same
[11:55] assets. So I have one link that has all
[11:58] of my core assets. They're agnostic of
[12:00] working with any of those models. So I
[12:02] can move around as needed.
[12:03] >> Yeah.
[12:03] >> Now with your question, codeex recently
[12:06] I've been running 60% of the time.
[12:08] Although I've been very loyal loyal to
[12:11] Claude Code for the vast amount of time.
[12:14] Claude Code is amazing at ideiation and
[12:18] planning to an extent. It's a visionary.
[12:22] >> It likes to go back and forth. It likes
[12:23] to judge you. But the one thing it
[12:25] doesn't like to do sometimes is follow
[12:27] the exact instruction in the exact way
[12:29] you gave it.
[12:30] >> So I see Codeex as a surgeon and Claude
[12:33] Code as a gifted artist.
[12:34] >> Yeah.
[12:35] >> And many times I have to bring in Codeex
[12:37] to look over the plan of Claude Code and
[12:39] I make them fight in a loop for 10
[12:42] different rounds until Claude Code
[12:45] finally has all the missing parts that
[12:47] Codex could see. All the things it
[12:48] wasn't anticipating.
[12:50] >> Totally. Yeah. I heard this tweet that
[12:52] or I saw this tweet that I thought was
[12:53] awesome and I want to see if you agree
[12:55] and I think you will because I have a
[12:57] very very similar philosophy to the way
[12:58] I I think about the two. But it
[12:59] basically said like it feels to me like
[13:01] cloud code is like a wise old owl. You
[13:04] can talk to it, you plan with it, it'll,
[13:06] you know, push back on you a little bit
[13:07] and then it feels like Codeex is like
[13:08] the Rottweiler that will grab onto the
[13:11] task and it will just it'll obey your
[13:12] commands and it will just keep going
[13:14] until it's it's done essentially because
[13:16] I think that the the verification loops
[13:18] inside Codex feel really really sharp to
[13:20] me. But um I think it's important that
[13:23] we kind of have that acknowledgement of
[13:25] you know which harness is best, which
[13:27] model is best. And it's it's more so
[13:29] which one is best for this specific
[13:31] task. Yeah, it might be, you know, a
[13:32] fivestep process, but for step one and
[13:34] two, maybe that's where you go for the
[13:35] codeex and then, you know, or vice
[13:37] versa. So, I think that's that's good to
[13:39] hear you say as well. Now, where do you
[13:41] see
[13:42] >> um you know, I think that Hermes and
[13:44] Open Cloud kind of get bucketed in
[13:46] together as well. Where do you see the
[13:47] differentiation there and you know with
[13:49] COD and cloud code as well?
[13:51] >> Well, with Hermes, what are you doing?
[13:52] You are bringing in the Hermes harness
[13:56] >> and you're just looping in whatever
[13:57] whatever model you want. So the reason
[14:00] why people have to really make their
[14:02] Hermes agent tailored to them, a special
[14:04] snowflake, is depending on how they want
[14:06] to use these models with Hermes, they
[14:09] have to keep hacking Hermes harness. Not
[14:12] this all these skill MD files, etc.
[14:14] They're all great, but the thing that
[14:16] made Hermes better than Open Claw is its
[14:19] harness. So with many tasks if you go
[14:22] one to one Hermes agent versus codeex
[14:25] you'll have a different result vanilla
[14:27] but you can eventually massage Hermes
[14:29] agents harness
[14:31] >> to do this verification loop that you
[14:32] mentioned earlier they really like about
[14:34] codeex is that it performs a very
[14:36] similar to it so you can do a level of
[14:38] monkey see monkey do.
[14:39] >> Yeah.
[14:39] >> So one thing that I did and you know you
[14:42] can go obviously no affiliation here
[14:44] it's open source. If you go to pi.dev
[14:47] dev, you will have this harness that you
[14:50] can bring onto your computer. You can
[14:51] copy with one command or if you're
[14:53] feeling daunted, what I did is I take
[14:55] this link, I feed it to codeex or cloud
[14:58] code and say go read the documentation,
[14:59] fan out some agents, learn about this
[15:01] whole harness thing. Once I do that, I
[15:04] can then ask it to go through what are
[15:06] called JSON L files. Basically, every
[15:08] conversation you have on your codeex and
[15:09] cloud code exists on your computer. So,
[15:12] I'll have it go look through all the
[15:14] conversations because they have the
[15:15] metadata of what tools were called, what
[15:17] verifications were done, in what order,
[15:19] and then I could have it monkey see
[15:21] monkey do. How do I start to make my own
[15:23] version of the harness that would react
[15:25] and do the same things based on similar
[15:27] types of tasks?
[15:28] >> You can start to reverse engineer all of
[15:31] the things that you love about cloud
[15:32] code and codecs. bring it to your own
[15:34] harness and eventually you can have one
[15:37] harness for everything where you bring
[15:38] in all these models as a brain that's
[15:42] leased you swap out as you need. So
[15:44] that's where I think we will get to
[15:47] where right now everything's tribal
[15:49] right YouTube is tribal X is tribal I am
[15:51] team CEX I am team cloud code I am team
[15:54] open source you all are Neanderthalss
[15:56] right for me I'm anti- tribal I am how
[15:59] do I make a system where any brain that
[16:01] could serve me for the best speed for
[16:03] the best rate at the best time can be
[16:05] swapped in with little to no acclimation
[16:08] needed
[16:08] >> so it's not a pain for me if Gemini
[16:10] wakes up tomorrow
[16:12] >> truly wakes up and now it becomes
[16:13] amazing saying, "Okay, it could probably
[16:15] take me 24 hours to swap everything to
[16:18] Gemini."
[16:18] >> Mhm.
[16:19] >> And [clears throat] I love that
[16:19] nimleness.
[16:20] >> Yeah.
[16:20] >> Because while Codeex is amazing today,
[16:22] Cloud Code might come cuz they're
[16:24] probably going to IPO sooner. Make a big
[16:26] push. And if we finally get a mythos
[16:28] that's not nerfed or neutered to
[16:30] infinity,
[16:31] >> you might want to move all your stuff
[16:32] there.
[16:33] >> Yeah. Yeah. And who knows what could
[16:35] happen from a price perspective as well
[16:37] for us as consumers. So I think that is
[16:39] really important to be thinking you're
[16:41] building out your own IP essentially and
[16:43] you need to make sure that you're
[16:44] protecting that and it's it's nimble. So
[16:46] I love that point there.
[16:47] >> Now you mentioned something earlier
[16:50] about making sure that your skills and
[16:52] your whole ecosystem is model agnostic
[16:55] and you have a special skill that you
[16:57] use to make sure that they can work and
[16:59] are optimized for different models and
[17:00] harnesses as well.
[17:02] >> What does that actual process look like?
[17:04] Because typically when we see like our
[17:07] skill files or folders, it's usually a
[17:09] markdown file and that's sometimes assoc
[17:11] or you know kind of like also has in
[17:13] there maybe a few Python scripts or
[17:15] whatever the skill does. Maybe there's
[17:17] some assets that go along with it but
[17:18] ultimately you've kind of got just like
[17:19] a master markdown file. So how do you
[17:21] actually make sure that codecs can pick
[17:23] it up and use it as well or other agents
[17:26] could pick it up?
[17:26] >> Absolutely. So the main thing to
[17:28] remember is that like you said all these
[17:30] skill files structurally look similar.
[17:32] They have this thing at the top called
[17:33] YAML where it's the name of the skill
[17:35] and what's called kebab case. You have
[17:37] the description and in the description
[17:39] you have a series of trigger words where
[17:41] when user does X I want you to invoke
[17:43] the skill to do Y.
[17:44] >> So what I did is I offload this. I asked
[17:47] codeex go and take a look at all the
[17:50] documentation from cloud code. Look at
[17:51] your own documentation. look at the
[17:53] documentation from let's say this
[17:55] specific other provider and go see how
[17:58] to build a versatile Swiss knife skill
[18:01] that will work for all of them as
[18:03] optimized as possible.
[18:04] >> Mhm.
[18:04] >> So Codeex prioritizes some things about
[18:06] skills that cloud code doesn't and vice
[18:08] versa. So how do we make sure that both
[18:10] are included? Now when it comes to
[18:12] scripts, Python is Python luckily. So
[18:15] that is already generic on its own. No
[18:16] need to worry about that. how you invoke
[18:19] that Python, how it knows when to use it
[18:21] and how to use it. That's where you
[18:22] might need to massage it a little bit.
[18:24] >> So even when I use this / poly skill, it
[18:27] will always look for these slight
[18:28] differences knowing ah codeex might miss
[18:31] this in the way that you're triggering
[18:32] it using cloud code. So let's make the
[18:34] description that much more beefier.
[18:37] >> So the likelihood that it picks it up
[18:38] across the board is much higher.
[18:40] >> Totally. So I just have AI do the dirty
[18:43] work to go see AI documentation and I
[18:46] update these monthly on a cron job. So
[18:48] every month
[18:49] >> I will auto audit audit my entire
[18:52] ecosystem
[18:53] >> refine all my skills see where I'm not
[18:55] using skills that I've added because a
[18:58] lot of people your audience and mine
[19:00] have bloated skill repositories where
[19:02] they downloaded some awesome skills
[19:04] thing they have 300 of them they load
[19:06] every single time and they use five.
[19:08] >> So it reduces the number of skills that
[19:09] I have. It combines the ones where
[19:11] there's an opportunity for a compound
[19:13] skill and then it makes sure that
[19:14] they're all model agnostic. I love that.
[19:17] Yeah. I think what's really important
[19:18] there is, you know, what you said, you
[19:20] have AI do the dirty work, but you are
[19:23] still very much in control and you still
[19:24] understand. And I always think of the
[19:26] quote, you can outsource the thinking,
[19:28] but you can never outsource the
[19:29] understanding. Mhm.
[19:30] >> And I think it's a great mindset shift
[19:33] to realize that
[19:35] even us as creators, a lot of the things
[19:37] that we don't know or that we need to
[19:39] learn, we have AI help us with it, but
[19:42] we still understand
[19:44] how to feed in like the documentation
[19:46] for it to look through and we understand
[19:47] now that it has this knowledge what to
[19:49] do with it. And I always kind of say
[19:51] this in my videos even though it might
[19:52] like hurt the views. Sure.
[19:53] >> Is that ultimately like just use it as
[19:55] your your thought partner as long as
[19:57] you're not outsourcing everything. I
[19:59] think that's a really important way to
[20:00] think about how you
[20:03] >> as a person continue to learn more too
[20:04] as well.
[20:05] >> Absolutely. And one thing you can do is
[20:07] again if we move into this world of you
[20:09] owning your own harness, you can have
[20:11] the same task be executed and then cla
[20:15] can watch it and it can run it within
[20:16] the terminal on your PI harness, run it
[20:19] on the other model providers, observe
[20:21] exactly what happened and what was the
[20:23] end result and try to continually
[20:25] understand and reverse engineer what
[20:27] happened with the others that's not
[20:28] happening with yours.
[20:29] >> Mhm. Back in March of 26, we had the
[20:33] cloud code harness leak. If you remember
[20:36] that, it was a map file. It was leaked
[20:37] to the whole world.
[20:38] >> I spent four to five days, and I I'm
[20:41] pretty sure you went and made a couple
[20:42] videos as well,
[20:43] >> looking through every single piece of
[20:45] it. Mhm.
[20:45] >> And the coolest part was the majority of
[20:48] the harness was full of all these
[20:51] crutches they gave to the brain, the
[20:53] model to not swear at the user to detect
[20:55] when you had swear words
[20:57] >> through a list of regex of all the swear
[20:59] words you would have that would tell the
[21:01] brain how to react. So once I saw there
[21:04] were so many crutches for this
[21:06] supposedly AGI level model, it made me
[21:09] wake up. Ah, this stuff isn't like ma
[21:11] troop magic at all. there is a whole
[21:13] factory of workers that are making this
[21:16] model look way smarter than it is.
[21:18] >> And as soon as you understand that one
[21:19] concept, that's when you snap out of it
[21:21] and you start looking at model
[21:22] benchmarks very differently, you are not
[21:25] as wowed by what bench it crushed.
[21:27] You're more wowed by how well the model
[21:30] provider do in now improving their
[21:32] harness to have a symbiotic relationship
[21:35] with this brand new model's brain.
[21:37] That's how that's why I care about
[21:38] empirical. How well does this do when I
[21:41] push it versus how well are they telling
[21:43] me it should perform based on how smart
[21:45] it is?
[21:46] >> Absolutely. There there's a question I
[21:48] wanted to ask you that I get a ton and
[21:51] um it it it revolves around this whole
[21:54] harness idea. It revolves specifically
[21:56] around this idea of
[21:57] >> building out your own second brain or
[21:59] OS. Mhm.
[22:01] >> The question that I get a lot is about
[22:03] as you every month are adding in new
[22:06] things, whether that be skills or um you
[22:08] know an LM wiki, how do you yourself
[22:11] make sure that it's staying optimized?
[22:14] And I put that in air quotes because I
[22:17] don't I truly don't believe that there's
[22:19] only one optimal way to do it. I think
[22:22] it's just a matter of making sure that
[22:24] you can feel when it's maybe searching
[22:28] too long for something that it should
[22:29] find right away or it's hallucinating
[22:31] information because of the bloat in a
[22:32] certain folder. So I would love to hear
[22:35] just kind of like dive into your brain a
[22:36] little bit.
[22:37] >> How do you think about keeping that
[22:38] organized and
[22:40] >> efficient? Sure.
[22:41] >> So the biggest thing that I've done is
[22:42] create what's called a rot.md
[22:45] file.
[22:45] >> Okay.
[22:46] >> Rot meaning decay. So if you have
[22:49] different layers of an AIOS and you have
[22:51] entire courses on this, you you covered
[22:52] this at length. You have five to six
[22:55] layers. One could be your identity, then
[22:57] your substrate, which is your core
[22:58] context that shouldn't change that much.
[23:00] Then you have your skills, your rules,
[23:01] your hooks, you have your agents, and
[23:03] then you have additional things you can
[23:04] add on. All of these different parts
[23:07] decay, become obsolete or rot at
[23:10] different rates. Mhm.
[23:12] >> So who you are, what you do, your goals,
[23:15] your aspirations unlikely to change very
[23:17] quickly.
[23:18] >> So you could have 1 to 3 months maybe
[23:21] even maybe longer if it's a company
[23:23] actually using this where it's relevant.
[23:25] >> Skills like I said I optimate up I
[23:29] update and optimize on a monthly basis.
[23:31] I just made a brand new one. [laughter]
[23:33] >> I like the word actually.
[23:34] >> And then you have let's say your rules.
[23:36] >> Your rules can change daily. I have
[23:38] rules that change daily because as I do
[23:41] new tasks with the same AIOS, I find new
[23:44] limitations and new edge cases.
[23:46] >> So I find ways to refine and make better
[23:48] skills that are more compound.
[23:50] >> My rules probably decay every week.
[23:52] >> Yeah.
[23:53] >> My hooks though, so things that it
[23:54] always checks. So if I push a client
[23:56] project to GitHub, it wants to make sure
[23:59] that there's a hook that fires to remove
[24:01] any PII, any sensitive data of that
[24:03] client that I don't want living on my
[24:04] GitHub.
[24:05] >> Mhm.
[24:05] >> That that might not decay for 6 months.
[24:07] I might change it a little bit, but it
[24:09] won't really be viable to be decaying at
[24:12] a very high rate. Skills and agents
[24:14] though decay incredibly fast to the
[24:17] point where Boris Churnney dropped a
[24:19] tweet saying you should delete all of
[24:22] your skills every 6 months. All of them.
[24:24] >> Did he?
[24:25] >> Do you know why?
[24:26] >> Why did he say that? Because a skill is
[24:29] basically an e extra crutch that we're
[24:32] adding to the system to help the brain
[24:34] do things or the brain better understand
[24:36] how to use all these tools to do the
[24:38] thing. But if the model truly gets way
[24:41] smarter, it might not need the skill to
[24:44] shortcut what tools to use at disposal.
[24:47] It might be able to accomplish the goal
[24:48] of the skill with purely a vague prompt
[24:51] versus the vague prompt plus the skill
[24:54] >> that's injected every single time. So
[24:56] you want to make sure that your skill is
[24:57] actually adding value and not holding
[24:59] back this dragon that gets only bigger
[25:01] with time and smarter with time and more
[25:03] powerful. So skills is one thing you
[25:05] want to audit very aggressively because
[25:07] you might not have a skill issue with
[25:10] that thing you built it for 3 months
[25:12] down the line, 6 months down the line
[25:14] with things like let's say agents. You
[25:18] hire agents like you hire employees. You
[25:21] might not always need a bookkeeping
[25:23] agent because if the model gets good
[25:26] enough, you might be able to give vague
[25:28] prompt. It would know exactly what are
[25:31] the 18 to 20 different subtasks based on
[25:34] all the memory assuming your memory gets
[25:35] better that it needs to execute.
[25:37] >> So we could live in a world where you
[25:39] have a handful of skills, a handful of
[25:42] rules, and those skills are actually
[25:44] very specific task at knowledge that it
[25:46] would never know no matter how smart it
[25:48] was versus step-by-step instructions.
[25:51] Wow. Yeah, that is really interesting.
[25:53] You know, I always make it a point to
[25:57] every time a new model comes out and I
[25:59] have, you know, I've got the new Opus
[26:00] model or whatever plugged into Cloud
[26:02] Code, I always make it a point to have
[26:04] that model run through all my skills
[26:06] just to make sure that it can use them
[26:08] in the same way and and things like
[26:09] that. But I have never thought really
[26:10] to, you know, I hadn't seen that tweet.
[26:12] I had I hadn't thought to go back to
[26:15] some of the like through all of them and
[26:17] say like, do we even need this? And what
[26:18] happens if you try to run that process
[26:21] without the skill?
[26:22] >> Exactly. So
[26:23] >> given your meteoric rise on YouTube, if
[26:26] I told you, hey Nate, here's how you
[26:28] make a YouTube video, right? Two years
[26:29] ago, this might have been a helpful
[26:31] skill for you to learn from me before I
[26:33] I started before you. But now I gave you
[26:36] that same play. You'd look at me, tilt
[26:38] your head, and be like, have you looked
[26:39] at our subscriber [laughter] counts?
[26:41] >> Right? You don't need this skill
[26:43] anymore. You have outgrown this skill.
[26:45] >> That's really interesting. So as a model
[26:47] becomes very diverse and has training
[26:49] data, you might not need the skill
[26:50] anymore. It might not it might be
[26:51] obsolete for where the model's at.
[26:54] >> Have you had an example yourself where
[26:57] you've been able to remove a skill
[26:58] because the model and the artist now
[27:00] just can crush it out of the water?
[27:02] >> Basically now if I tell it go and read
[27:04] all the conversations that we've had and
[27:07] tell me 15 different things we can
[27:08] optimize. Mhm.
[27:09] >> I used to have a skill that would tell
[27:11] exactly where to look for the files that
[27:13] are associated with our conversations,
[27:15] how to break it down so it doesn't blow
[27:17] its context window with 50,000 tokens at
[27:19] once times 100.
[27:21] >> I used to have to really explain that
[27:22] bit by bit.
[27:23] >> And now I went from skill to now we're
[27:25] moving to skill and now I have one basic
[27:28] sentence and it knows exactly to
[27:30] optimize based on my cloud. I'm always
[27:32] trying to optimize my uh context window
[27:34] and my context use. it on its own can do
[27:37] that without me telling it to.
[27:39] >> That, you know, that makes me think of
[27:40] something that's that's really
[27:41] interesting because of that ability for
[27:44] it to be more creative and arguably a
[27:47] better problem solver because it knows
[27:48] how to get to that end goal. Mhm.
[27:50] >> That might also be kind of a scary thing
[27:54] because in some cases maybe the skill
[27:58] keeps it on stricter guard rails
[28:00] >> potentially
[28:01] >> because sometimes now if it has to try
[28:03] to find its own way to from point A to
[28:05] point B, it might try to create some
[28:09] things that could potentially be harmful
[28:11] to the system or something like that as
[28:13] well.
[28:14] >> But that's where the rest of the AIOS
[28:15] comes in because like the AIOS is not
[28:18] just a skill. You have the rules, you
[28:20] have different layers to babysit.
[28:22] >> So we might live in a world where we we
[28:24] need way less skills and much stricter
[28:27] rules. And your cloud MD now just
[28:29] basically says go and follow these rules
[28:32] for these kind of situations
[28:34] >> and that could be sufficient enough.
[28:35] >> Yeah.
[28:36] >> So some of these layers, even the
[28:38] concept of assigning an agent and
[28:40] creating your own agent that's all spun
[28:42] up the same way every time, that could
[28:43] become obsolete. So, I'm not saying it
[28:45] is, but I'm saying we should be
[28:47] open-minded that this stuff will evolve
[28:49] and as long as you keep your core assets
[28:51] nimble, then you should be good to go. I
[28:53] love that. You know, I did see which I
[28:57] thought was really interesting. I don't
[28:58] remember if it was Opus 5 or Fable 5,
[29:01] but one of those drops
[29:02] >> from Enthropic, you know, how they
[29:04] dropped the blog with benchmarks and
[29:05] just like how to use it, how to prompt
[29:07] it.
[29:07] One of the things I remember being at
[29:09] the top was
[29:12] give it more ambitious tasks. And you
[29:15] might just skim through that, right? But
[29:17] to me, that made me think, well, why do
[29:19] they feel the need to put that in there?
[29:21] Maybe they feel like people aren't
[29:22] pushing the models to their true limits
[29:25] and getting out of the model's way. And
[29:26] that's when I started to run these just
[29:28] interesting experiments. I'd set a SL
[29:29] goal and I'd say like kind of something
[29:31] along the lines of like impress me like
[29:33] build me build me this but impress me
[29:35] and show me what you can really do. And
[29:37] I just thought that that was interesting
[29:38] that they put that in there and it just
[29:40] shows like that kind of makes me think
[29:41] that whole skill thing like the skill
[29:42] that we we maybe have baked in a long
[29:44] time ago and now we just kind of blindly
[29:47] use because it it works. we are almost
[29:50] yeah kind of
[29:53] baking in or or limiting what the model
[29:56] could truly do because it's it's kind of
[29:57] going down these these guardrails. So I
[29:59] think that's that's really interesting.
[30:01] You know, as we sort of start to wrap up
[30:03] here today, I'd be interested to hear
[30:04] from from you. What is something that
[30:08] you think that you do within your
[30:11] cloud code or your harness setup that
[30:14] most people don't do and that you think
[30:17] is important that everyone should be
[30:18] doing?
[30:19] >> So the main thing I think about is many
[30:22] times I have let's say 25 different
[30:24] operating systems.
[30:26] >> So some people like to create one big
[30:28] one.
[30:28] >> I create very specific ones that live in
[30:31] an isolated world.
[30:33] >> Okay. So my tax and finance lives very
[30:36] differently from my consulting OS which
[30:37] is very living very differently from my
[30:39] school OS for content for there versus
[30:41] everything else.
[30:43] >> So me segmenting every single part of my
[30:46] business my education offers everything
[30:49] we do for enterprise clients each thing
[30:51] has its own set of operating systems.
[30:54] >> It's more to upkeep for sure but as you
[30:57] build more you start to build more
[30:58] leverage. So I have one mega system that
[31:01] depending on its audit of every single
[31:04] operating system I have will come up
[31:05] with a series of things that we need to
[31:07] make that specific thing better that
[31:09] specific operating system work better
[31:11] and one that generalizes across all of
[31:13] them.
[31:14] >> So as you create different folders
[31:16] you'll have some project level skills
[31:18] rules cloud and then global. Mhm.
[31:21] >> Some people make everything global,
[31:23] which is awful because as you add new
[31:24] things, you might notice under
[31:26] performance cuz you forgot that you have
[31:28] this global spectre of rules applying to
[31:31] every single thing.
[31:32] >> So for me, I have a different concept
[31:34] where I think about promotion.
[31:37] >> Everything is project until deserves to
[31:39] be promoted to global so that I know at
[31:42] all times what is the running total of
[31:44] everything that's running globally.
[31:46] >> And I have a very few number of things
[31:48] that are global. Everything's project
[31:49] specific. But that also gives me this
[31:51] the flexibility to have a very small
[31:54] blast radius if I want to be
[31:56] experimental. If I want to audit and
[31:59] push a certain folder for a certain type
[32:01] of task and not have that bleed over to
[32:04] another project and not know why is this
[32:07] not working, is the model worse? Is the
[32:09] harness worse? Or is my setup worse? So
[32:13] because I'm so meticulous about is this
[32:14] a model problem, is this a harness
[32:16] problem? Or is this an organization
[32:18] problem? when I can isolate things, I
[32:21] can find the issue faster.
[32:22] >> So, Fable is amazing with my tax, but
[32:26] all of a sudden, it is horrific with my
[32:29] consulting operating system.
[32:31] >> It might not be a model issue.
[32:33] >> It might not be a skill issue. It could
[32:35] be an organization issue for that model
[32:37] that I might have to adhere to for this
[32:38] specific project.
[32:40] >> And that helps me control bloat and find
[32:43] the area of resistance that I need to
[32:45] move to actually get the reforms I'm
[32:46] looking for. I think that's really
[32:48] smart. I think especially because these
[32:50] things are so so autonomous and agentic.
[32:54] >> You have to be able to
[32:57] find the actual variable that that
[32:59] killed the thing. Otherwise, there is no
[33:01] learning there and there's no
[33:02] improvement there.
[33:03] >> And it it it for the most part you can
[33:06] help like it can help you find out why
[33:08] it went wrong and where. But I think
[33:10] that level of isolation and I think the
[33:12] key is there that you know how your
[33:15] different folders are drilled down. Yes,
[33:17] >> you know, you're not just blindly
[33:18] trusting that it can find everything.
[33:19] You still intuitively
[33:21] >> I have a feeling that if you are looking
[33:22] for a specific deliverable, you could
[33:25] find it just by clicking through your
[33:26] files and folders because you kind of
[33:27] know where the things live and you know
[33:29] how to drill down.
[33:30] >> Yes.
[33:30] >> And I think that that's just highlights
[33:32] the point again that you cannot
[33:33] outsource your understanding. You still
[33:34] have to understand where everything is
[33:36] and how it works.
[33:37] >> Yeah. The last thing I was going to say
[33:38] is that this becomes an acquired skill.
[33:41] And if you want to get to mastery,
[33:44] mastery is just understanding how the
[33:45] entire factory works end to end and
[33:47] where each piece lies. So if you want
[33:50] more leverage, if you're running into
[33:51] issues where you're kind of being
[33:52] intellectually lazy and saying, "Oh,
[33:54] this model sucks." Before you pass fully
[33:56] judgment on it, you want to make sure
[33:58] that maybe it sucks, for the setup that
[34:01] you currently have. So when in doubt,
[34:04] audit your setup, audit your skills,
[34:06] audit the bloat because different models
