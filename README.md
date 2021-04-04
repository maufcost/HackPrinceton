# The Vortex: A Smart Social Network. All events around you. All perspectives around the globe.

## Why was the Vortex created?

**The Vortex** was created to catch **every** angle of an experience, so you don't miss out on anything. 

## What does the Vortex do?

**Vortex is a smart social network** that allows people to share their best moments captured in an event by uploading videos of their perspectives of the occasion. The web platform uses machine learning to find the best viral moments in a collection of videos and then automatically generates a highlight video for an **entire community or event**. You can even search videos by words or objects that might be in them!

## How did the Vortex team created the Vortex?

The Vortex and its smart social networking features were created with continuous care and delicacy. Its front-end was meticulously crafted using HTML, CSS, and Javascript. All the icons and logos were also created **from scratch** using Adobe Photoshop, Illustrator, and Premiere. 

The Vortex's back-end was mesmerizingly built using a Flask server on top of Python and Google Cloud App Engine. All of the user data, including event details, video details, and posts are securely stored on Google Cloud Datastore. The video and gif files are stored in a Google Storage Bucket with triggers to Cloud Functions. Every time, a user uploads a video in The Vortex, a Google Cloud Function is triggered and The Vortex begins analyzing the video with Google Cloud Video Intelligence to find relevant labels and their respective timestamps. 

After the video is analyzed, we save a gif thumbnail of the video and The Vortex saves all the data inside Algolia API for easy search and indexing. After The Vortex reaches enough clips, it uses the machine learning data in Algolia API to automatically create a video in the cloud using the VEED API.

## What were the challenges that the Vortex team came across?

Continuously analyzing the shared videos from people all over the world in the Vortex is no easy task. At first, we thought we wouldn't be able to accomplish that in a timely manner because of the amount of **video analysis and artificial intelligence research and applied machine learning study** needed; however, we proved ourselves wrong and the **Vortex is now alive** in a cloud somewhere in the world for anyone to watch and share! 

The hardest part of the project was utilizing the Cloud Functions with the Storage Triggers combined with Google's Video Intelligence API. It was our first time dealing with Cloud Functions so we had to deploy our code multiple times before it finally worked. In addition to that, The Vortex generated so much data that the Algolia API was giving us errors for passing the limit. As if this was not enough, the resources for cloud video editing are very scarce so we had to spend a lot of time trying to come up with an automated solution to bring the highest quality to The Vortex.

## What accomplishments is the Vortex team proud of?

Since the beginning of the Vortex and its social networking ideas, we aimed at providing a user interface and experience that would make people feel as if **they are contributing to something bigger than themselves**, and the Vortex team is proud to believe that we accomplished such task. Also, as we said above, researching video analysis and applying artificial intelligence to study shared videos in the Vortex in such a short amount of time brings us countless smiles on our faces :)

## What we learned by creating The Vortex?
The Vortex team reinforced to themselves that if you put your mind at a direction, think obsessively about it, and, most importantly, act upon your ambitions... boy, **you can accomplish anything**. _ The Vortex is an inherent proof of that _.

## What's next for The Vortex?

The Vortex has an innate capability to spread throughout the world. We are aiming to improve the **Vortex's sharing capabilities**, where you can share specific perspectives from others in the Vortex with others outside of the Vortex. The Vortex team is also looking forward to improving our overall machine learning algorithms and allowing users to create their **own local Vortexes for their own shareable memories**.
