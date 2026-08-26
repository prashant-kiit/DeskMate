# Interview Q&A Extraction

**Source:** parakeetai_prashantsingh090798_gmail_com_AI_Engineer_24-08-2026.txt
**Role:** AI Engineer | **Date:** 24-08-2026 | **Speakers present:** Interviewer 1, Interviewer 2, Interviewee, and an "AI" channel

> **Note on the "AI" entries:** The transcript contains blocks labelled `[time] AI` (ParakeetAI assistant-generated suggested answers). These were **not spoken** by the Interviewer or the Interviewee, so they are never recorded as an answer below. Where one occurs against a question, it is flagged as *"AI-assist suggestion present (not spoken by either party)."*

---

## Question 4

**Question:** "So can you tell me about some of the projects that you have working on? Like which one is your favorite?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "So last AI project, which. I worked upon was a rack pipeline where, uh, internal users were. Uh, allowed to write a query against the internal documents, which were present on confluence and based on the query, the result, which was the result which came, was augmented by the confluence documents, which were already there in the knowledge base of the of the company. And this included, uh, ingestion pipeline, uh, based on an automated job, which fetched the latest version of the documents from confluence and chunked it. And. Chunked it based on internal structure of the documents, headers and subheadings, points. And then ingested it into a vector DB. After, uh, tokenizing them. Using an embedding model and the query which came, uh, also got, uh, you know, tokenized and embedded into the model. And against that query, a similarity search was performed between the query and the already ingested documents. And. Uh, result was returned and. And the output was reranked based on the, uh. Um, the similarity score, the higher. The highest similarity scores. Uh, um, documents were used as a context into the system prompt. And that system prompt went into the LLM and the result was returned. The result returned was again reevaluated by another agent. Uh, it was a separate agent, primarily with a high higher model, particularly. Made for, uh, evaluating the response once the evaluation is done and a certain score has been achieved. Then only the response would be sent back to the user in front end. Otherwise, the same, uh, you know. The process. Cycle retrieval and regeneration cycle would again happen to. Handle data in [interrupted] vector DB. We kept, as I said, a. Metadata was stored based on the created. Uh, I mean created date time and beyond a certain threshold date time. Those, uh, those documents were removed and a new document would be placed in front of them. Because of that automated job."
*(Response is interrupted mid-sentence by the Interviewer's "Okay. So." and by Interviewer 3's "I"; the Interviewee continues afterwards — preserved as-is.)*

---



## Question 5

**Question:** "So what was the similarity algorithm that you used for retrieval?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Similarity algorithm was hierarchical, small world. Navigation. Based on that, we did. It was, uh, we used a library, not we didn't build it ourselves. But we studied it and understood the advantages of it. And based on that's why we chose that algorithm. The advantage is mainly, uh, that it doesn't have, since it is divided into various small worlds, which are nothing but the various hyperplanes built on the top of, uh, graphs. Where each node is a vector and, uh, edges. And they are connected across edges and that's how a graph is formed. And since they are divided into hyper divided by hyperplanes, into small worlds, the most, uh. Loose, most. How to say that the least, uh, at the start of the search, the least closest node is captured first and, and it goes down the, uh, the hierarchy of the small worlds to get to the get further close to the most, uh, apt node. So advantage is that it doesn't, it doesn't have to go linearly as in, uh, linear vector search. So it would save time and would reduce it from linear search to algo to algorithmically and time of search would happen. And thus the time would be saved. And, and the, and we even, even though it would not be as exact as linear because. Because it would start. Because it would start from centroid based searching. That's why. But that was okay for us because, uh, exact, uh, exactness was, uh, not that important at the speed for us and for. Exactness. Good retrieval process. Procedure was used so that the, um. That whatever response comes is based on the documents. So we manage that as I said. Right, through using another self-correction agent. So hierarchical small world. Similarity helped us to prevent the latency by. Logarithmic search and the uh, agent. Self-Correction agent helped us to make sure that the accuracy is there."

### Counter-Question 5.1

**Question:** "But in this case, since you use. And it's an optimization algorithm. So why why did you go for exactly this? Like have you tried out locality sensitive hashing in this scenario?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Your voice broke. I couldn't hear the question." *(incomplete — question not heard)*

#### Sub-Question 5.1.1

**Question:** "Uh, is it better now?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Yeah. It's fine now."

#### Sub-Question 5.1.2

**Question:** *(question restated)* "Yeah. So basically I'm asking like, why have you tried out locality sensitive hashing instead of w? I mean, it's an optimization algorithm, right?" — clarified as "Locality sensitive hashing." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Locality search. Uh." … "Okay. Okay. So." … "That could have also been used, but we went because. See, uh. High in. In that case, um. Uh, in in that locality hashing the, uh, the vector space is randomly divided by hyperplanes. So. So, um. I mean, to me, uh, random division doesn't, make much sense. So I went with hierarchical, small world. Because that kind of indexing would, uh, make much more sense because, uh, vectors which are close are closer to each other would have similar meaning. So making sense. And making a nodes of the centroids with similar meaning making graph of the nodes of vectors having similar meaning makes much more sense than randomly dividing them across planes."

### Counter-Question 5.2

**Question:** "And since you're already diving into hyperplanes, right. So. You tried out. Other such indexing." *(Interviewer 2 — functioning as a question)*
**Interviewer's Answer:** "Uh, yes. Basically randomly divides the hyperplanes. But that does not mean that the hashes will be very far off. Right. Like it is same locality sensitive hashing because the hash of that vectors. Similar vectors would be pretty similar." and "Right. You use the hash collisions to get the bucket. So basically let's say two vectors are very similar to each other. They will fall under a same bucket." Later: "Yes, it's basically that is more efficient compared to LSH and can be way more complex to implement. But the natural W it mainly depends on how you are creating that world. The small worlds, what leads to the next depth? You know."
**Interviewee's Answer:** "Correct? Correct." and later "So I in that question, I just want to know that I know what, how those two algorithms work and, uh, and I have knowledge over those two. And I could explain that. And deliberately we chose the hierarchical small world. Navigation because we felt that I provided you the reasons for that. As per my understanding." Then: "Yes, yes. So the small ones were based on the closeness of the vectors in the, uh, in the. Vector space. Similar ones were kept together. So that was the idea."

### Counter-Question 5.3

**Question:** "So you want to know why we did not choose that over, uh, small, hierarchical, small world?" *(asked by Interviewee)*
**Interviewer's Answer:** "Uh, no, no, that is fine. Let's move on. So, uh, for the lexical part."
**Interviewee's Answer:** No Answer *(Interviewee is the asker)*

---



## Question 6

**Question:** "So, uh, have you done some? Fi or PII reduction [redaction] in your projects?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Yes, yes."

### Counter-Question 6.1

**Question:** "So let's say you have a constraint that you cannot use the. LM. Okay. Not, not an LM. So you can use LM. Uh, think of this use case where LM is hosted on a third party server. Okay, so third party server cannot access. Di or any kind of PII. So in this scenario, let's say you have a completely NLP document. It can be, uh, you know, a PDF, it can be text, it can be, uh, image. Now when you're doing processing that kind of document, maybe let's say you are doing a summarization in that scenario, how will you prevent the Phi from going there? Like I don't need it to be 100% accurate all the time, but let's say I want it to be at least 90% accurate." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Okay. So we will, we will have a vector DB, which will be self-hosted and will not be using any third party so that the data security is maintained. And on, on that vector DB, we will store our documents. And the similarity. And the. And we. And we need to identify the pH. We need to filter out the pH. So for that. Also, we need to have some other document which would mention, uh, uh. What kind of what are the PPIIS we are what we are. Uh. Trying to avoid the kind of PII, are redaction, which we have done, uh, in. Included all included the name of the users, their address and, and their address, their addresses, name and various kind of personal details, which was already there in Postgres database. Our application database. Apart from that, we also did pH. I redaction, which meant that, um, any kind of medical details, such as, um. Uh, medicine name or any company name, which is related to medicine should not be appearing in the trans in the response. So that detail also we had from a. From a third party, uh, website. Which, which was storing all kind of, uh, medical. Company names and medical. Medicines. So what we did, we ingested data from there and stored it in vector DB. So medical details, which needs to be avoided. We had in the. Our DB and also we had our personal details already in Postgres database. So and. And the documents from which those, uh, those PII and Phi needs to be reduced needs to be removed where they are in the vector DB. So first, first. First, we would query the Postgres DB and the database where phi has been stored and, and based on that, we would we would query, uh, the vector DB in such a way that all the, all those documents which are having those details will be removed, will not be coming out as a document in response."

#### Sub-Question 6.1.1

**Question:** "Okay. So so I got that, uh, just few questions. PDF. The document is are in PDF and you said that we are not allowed to use LLM." *(asked by Interviewee)*
**Interviewer's Answer:** "Uh, it can be in PDF, it can be in images. It can be pure text. It's multi-modal system."
**Interviewee's Answer:** No Answer *(Interviewee is the asker)*

#### Sub-Question 6.1.2

**Question:** "It can be in multi modal formats and we cannot use, uh. LM is that what you said?" *(asked by Interviewee)*
**Interviewer's Answer:** "And, uh." … "LM will be used. It's just the phi or the PII will should not be sent to the LM."
**Interviewee's Answer:** "Okay. Got it. Okay, okay."

#### Sub-Question 6.1.3

**Question:** "So you want us to, uh, identify Phi without, uh, without using any. LM but we can use vector DB, right?" *(asked by Interviewee)*
**Interviewer's Answer:** "Yes."
**Interviewee's Answer:** No Answer *(Interviewee is the asker)*

### Counter-Question 6.2

**Question:** "But how? Uh, yeah." — then redirected: "No, let's change the, um I think that that part, uh, I'm not asking you to block the request. I want you to redact the request. So let's say I give you a prescription, right? In prescription. My name is Pharmagenus. But in real life will not be using the full name all the time. Let's say we, the doctor will assign the prescription, give it as does. In that case, I think your Postgres will not match, right? Because there is a name mismatch. And you'll have to put some regex rules such as first, uh, first letter or those initials, those kind of things. But in this case, uh, you are using cosine similarity or let's say any kind of similarity algorithm. But you are getting a similar document. You're not getting, whether it contains a picture or not." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "So the chunks which have the PII, the. Suppose the document against which the response needs to be augmented. Uh, the chunks of those document which have PII should be avoided and should not be sent into the LLM to." *(interrupted)*

### Counter-Question 6.3

**Question:** "Yes, but can you think of it? Because. Let's say you don't. You have some, right in your Postgres. But in the prescription does. Now, s I don't think will be matching with anything right in your face." *(Interviewer 2, after clarifying "no. Only the PII should be redacted. Not the chunks. Chunks can have important information.")*
**Interviewer's Answer:** "But it will match with anything that actually is similar, right. Because vectors are not really like they are for similarity match. They are not for differentiation. Or classification. Generally."
**Interviewee's Answer:** "The, I mean, if a particular chunk. Suppose the chunking is done on the basis of a word, and that word has your name, Swamiji. And that chunk should be avoided." Then: "First we. If we pull it from Postgres and then, uh, make make it go through an embedding model and turn it into a vector and then use that vector to do a negative to, to a, to do a negative search. I mean, search where that vector. So vector is not equal to the document. The document chunks. Then all the chunks which do not have some edges would be coming out even since it's a vector match vector similarity match even the the. The the exactness of the name is not required."

### Counter-Question 6.4

**Question:** "Let's say you, uh, but it will also lead to a huge vector chunk. Every single user, every single user's information, information can not only be name, it can also be, you know, address, it can also be payment information. And it's not that you will always have the information in your Postgres. It can be a user who is not in your system. The document that you're processing. Also, it can be from a party like the doc name or the company name, which you don't have access to or you have not heard of. Do you think like, can you think of any other way in which it can be handled?" — with hint: "Just giving you a hint. You don't have to use GP. You can even use CPU inferences for something." *(Interviewer 2)*
**Interviewer's Answer:** "Yes. Uh, I mean, since, uh, you don't have access to LMS, right? For this for reduction." and "Why you don't have access to LMS because elements are expensive to host. They need GPU. But there are some things which can be hosted even on CPU or like the corporate EC2 instances, which are pretty lightweight."
**Interviewee's Answer:** "Okay." … "C I can avoid GPU and use CPU." … "De" … "I mean, if we use CPU, then we must be using some kind. We need to have some kind of a. And we would be avoiding any kind of vectorization."
*AI-assist suggestion present at this point (not spoken by either party).*

#### Sub-Question 6.4.1

**Question:** "This is breaking. Uh, can you repeat your last sentence?" *(asked by Interviewee)*
**Interviewer's Answer:** "Yes. So the hint is. Basically, you do have to always stick to GPU. You can also use a CPU inference. So can you think of something that can help you out in this scenario?"
**Interviewee's Answer:** No Answer *(Interviewee is the asker)*

### Counter-Question 6.5

**Question:** "You can do vectorization even on CPU. I mean, have you heard of the algorithm in bag of Words? Vectors does not always have to be semantic. You know. You can even do CPU based recognition." — followed by "Okay. Like for example, from. It's a very specific class of models. Which are, I mean, they are mainly used for this kind of situations." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Lightweight. Um. Category. Categorization. Uh, models." … "Like one such, which I have used, which I can remember of is Microsoft Presidio. Uh. And, uh, that library basically that provided NLP, which will be used for, uh, categorization of such. Tokens." … "So that I, I mean, named entity recognition, something like that is it's called." *(Interviewer 1 interjects "Okay.")*
*AI-assist suggestion present at this point (not spoken by either party).*

---



## Question 7

**Question:** "So, uh, is there. Another project that you have worked on as well, except like something like chatbot or a system." *(Interviewer 2)*
**Interviewer's Answer:** "Yes."
**Interviewee's Answer:** "Engine. I have worked upon." *(incomplete — refers to a recommendation engine)*

### Counter-Question 7.1

**Question:** "Okay. So, uh, can you like what you were doing in that recommendation system? Like, what was the flow going on inside?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "So let me give you this context. So it was a social media platform. Um. For a, for businesses which are involved in sustainable development. So. So our, our recommendation engine was job was to, show the post to the user, which are related to its user activity, which are similar to its user activity. So our first job to record all the user activities which are happening on that application for particular user. And based on that, we used to show the posts to that particular user on the first on the first home page itself. So for that, we, uh, developed an recommendation engine. So the main, the whatever, um. So for that, we needed to divided divide each post into certain means. We need to identify certain attributes of each of the posts. Such as, uh, what kind, what kind of business domain it is into, uh. And what are the preferences of the user and in. What region? Uh, um, I mean, is the post, which is there, is it talking about a particular region or a particular time? So based on that, each post had certain attributes and based on that attributes, uh, and those attributes were stored in the user activity log and those user activity logs were then again used for each of the to. Match against the attributes. Same attributes stored in. Each attributes of the post or in the database and. Whatever similarity was found and the highest. The post with highest similarity were returned. As a response um to be. Displayed in in the home page. To be specific. Uh. Suppose one of the metric which was chosen was uh, suppose a business domain a user has been, uh. Liking posts which are of particular, uh, suppose automobile industry. So. So that user. So the user, whenever he likes. Uh, a post or particular, uh, of a particular business domain. I mean, all the domain would be recorded. So, so this particular user database would show like this particular user had liked this, uh, post and that post belonged to use automobile industry. So that's how the record of a user activity looked. Now whenever and there would be n number of posts on the social media platform for, uh, automobile industry. So all those posts were stored in a separate table in the database. And each of those posts would have, uh, the business domain mentioned. And the, the post, which had business domain as automobile would be filtered. Uh, for that particular user and displayed. So, so that's how we did. And for this. So, so for this, we didn't use, uh, LM. It was a. I mean, it, it, it was a, a deterministic platform. There was no. LM involved normal database query, which we used to do. So."

### Counter-Question 7.2

**Question:** "And have you, uh, tried? I mean, so you did not try any kind of vectorization here, like vector mathematics. In this system." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "But that that would um if we do that then uh. See the exactness would be again lost. Right." Later: "So we can use vectors for deterministic. Uh, filtering. But uh, but instead of C, we would, we are consuming compute in changing a normal. Uh, database record into a embedding into passing. We are passing it through an embedding model, changing into a vector." Then: "Got. It, we can directly make it into a vector. Got it, got it." Then: "Generally the AI use case. I what I think AI use case should happen when we have a. We we want to target something non deterministic. If something is already. We can do something using traditional software engineering, then using AI capability over there."

#### Sub-Question 7.2.1

**Question:** "Vector mathematics for doing similarity for domain matching?" *(asked by Interviewee)*
**Interviewer's Answer:** "I mean, because domains are nothing but, uh, like what is basically vectors are basically an array of zeros and ones, right? It's a dimension." and "So let's say you have multiple n number of dimensions. Each dimension is belonging to one attribute. One can be advertised. One can be a movie show. It can be a movie show as well as about automobiles. So based on that you can create a vector out of that post. And use maybe Euclidean distance into getting the best matching post to that specific thing, right?" Then, to the "exactness" objection: "No, because, uh, exactness won't be lost because the post will always have a fixed attribute. A car. Advertisement will never become a book. Advertisement. As long as the vectors are same, the similarity will also remain same. And vectorization is actually a deterministic function." Then: "No, we are not passing it through an embedding model. We are passing it through an embedding function. You develop that function. Embedding does not need always to be semantic, right?"
**Interviewee's Answer:** "Yes."

#### Sub-Question 7.2.2

**Question:** "But that what benefit it would bring over. Uh, normal DB filter." *(asked by Interviewee)*
**Interviewer's Answer:** "So basically. Uh, with normal DB filter, the issue is you have to maintain a huge set of tables. Everything gets its own table, right. And instead of that, you can have vector db in which each vector has multiple dimensions. And you can have multiple vector metrics such as Euclidean distance. You can use stopgap. You can build a basically, uh, runtime classifier on top of it. If you have vectors."
**Interviewee's Answer:** No Answer *(Interviewee is the asker)*

#### Sub-Question 7.2.3

**Question:** "Uh, does that make sense?" *(asked by Interviewee, about AI being used only for non-deterministic problems)*
**Interviewer's Answer:** "AI does not always have to be. Large or large models. Even the smallest. Like Bayesian network. That is also, uh, I mean, it's not exactly AI. It's a, statistical machine learning algorithm. You can have a network, you can have even a small linear regression classifier. Like those are also AI kind of. They are basically deterministic."
**Interviewee's Answer:** No Answer *(Interviewee is the asker)*

---



## Question 8

**Question:** "Have you used any kind of, uh, hybrid search in your rack [RAG] systems? So basically in rack system, there are two searches. One is the vector search and one is the lexical search. So have you used a hybrid search in your [RAG]?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Yes." Then: "So hybrid search, I mean, wherever. Most of the time I prefer using hybrid search because, uh. First, first to save the compute, I go with the hybrid search. I mean, first I go with the term based or exact search so that only those documents are fetched in a rag. I'm talking in the context of a rag. Only those documents are fetched, which, uh, which are exactly matching to the certain keywords in the query. And, and on top. And once those are, uh, retrieved against that, I tend to do similarity search on the semantic search of whatever kind."

### Counter-Question 8.1

**Question:** "Okay. And so you. Basically first run the lexical search. And once you get the lexical search, you run the uh, similarity search on the results, right." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Yes. That is one way. Another way is to do both of them simultaneously. And then, uh. Fuse them at the end and whatever ranks the best based on both their rankings, whichever ranks the best return that."

---



## Question 9

**Question:** "What was the lexical search algorithm that you used in your hybrid search? Can you." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Lexical search where, uh, mostly based on, uh. We made, uh, we. We, we embedded the documents using tokens. So we use. Token exact matching to do so. So whatever query came, uh, their keywords were picked up and, and they were tokenized by the same embedding model and against those. And then those, tokens were chunked out into various chunks and. That chunks were used to do exact similar exact term based searching against the documents in the vector DB."

### Counter-Question 9.1

**Question:** "Okay. But like what kind of search that was it basically just a, uh. Type of check or, you know, like just contains check that kind of term or do you have something different? And there are a lot of, uh, term based algorithms like, uh, you can do fuzzy matches. You can do Levenshtein." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "It was. It was token based and it was exact. It was not Levenshtein based. Levenshtein I have done in another project for fuzzy searching, but the one in which Rag was involved. I did uh, token based exact matching, no fuzziness was involved." Then (added after the Interviewer's next prompt): "So we. Did another project where, uh, a list of, uh. Lists, which was basically a dashboard where, a list of insurance policy needs to be searched out using a search bar. So therefore, to handle them, the misspellings and Misspells. And, uh, you know. Words not arranged in a proper format. To, to do that, we use, uh. Fuzzy searching."

---



## Question 10

**Question:** "Okay, let's say I give you one scenario. Can you tell me like, what is the weakness? Uh, like, can you think of any weakness of the approach that you gave? Like, can you think of any failure scenarios where you're doing a lexical search first and then running the vector search?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "It it increases the latency. We are doing two kind of searches, one after the another."

### Counter-Question 10.1

**Question:** "Any scenario in which it can lead to loss of data. Actually. Like you're not retrieving the proper or enough context." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "It can, um, uh. See it since it is exact, uh, it doesn't term based searching doesn't take into consideration of context. So it can lead a loss of context. And if we lose the context, then the responses might not be correct."

### Counter-Question 10.2

**Question:** "Okay. And also like, maybe the user can make a typo or you can user can use an abbreviation as well. Let's say you build a medical database of a query engine and, uh, you know, the chunk that you've stored or the chunks that you have scraped from the website contain influenza. Okay. They are maybe thousand page chunks you have from influenza. But the user asked a question about, you know, flu. In that case, what you miss the entire influenza context." *(Interviewer 2)*
**Interviewer's Answer:** "Because you are not." *(incomplete)*
**Interviewee's Answer:** "Yes. Correct." Then: "That both similarity we used hybrid search where both semantic and lexical search were done parallelly and whichever documents. Uh, and we did, and when fused the result and we did the reranking at the end. The reranking was the summation of the ranks of both. So whichever tops in in that summed up rank that was returned. So that would that would mitigate that kind of issues, which you mentioned."

### Counter-Question 10.3

**Question:** "Can you use like, can you think of any other way of mitigation? Because it will not always lead to a mitigation. Because what happens? Basically, a vector search can bring up the relevant chunks. But, uh, the lexical search, it might not bring up the relevant chunks. It can instead pull it down. The final result. Because you take both of them into consideration, right? Can you think of any way, uh, where you can hit those missing chunks or increase the search space for vector search? Because if you are doing using, you know, like only a user query, two vectors, it can and will lead to a lot of missed information. Uh, when you, when you, if you see something like OpenSearch, OpenSearch has also launched. Um, rag engines, uh, vector DB. So if you go to bedrock, they also implemented a very smart approach in which they can avoid those kind of issue. Can you think of any way in which you can, you know, like handle missing context or a context being a little bit, but pretty similar to the user's query?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "So. One way is, is to, uh, handle this can be to not divide documents into very small chunks. And suppose there is a document and we can use their internal structure. Such as headings, subheadings, and based on that we can divide it. So that would since the chunks are not very small. Uh, that would prevent uh, losing out of context."

### Counter-Question 10.4

**Question:** "Anything else like you, I'm not talking about like making sure the user's query itself is becoming wide. Can you have a NLM [an LLM] that basically does a query expansion in between before making the vector search, the user gives you the element can treat the flu and convert it into a common cold or similar names of the disease. That can give you a better retrieval." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "That that can be one way. Correct. I understood that."

#### Sub-Question 10.4.1

**Question:** "Okay. So you okay, you are saying that we need to rewrite the query which came from the user, and then based on that." *(asked by Interviewee)*
**Interviewer's Answer:** "Yes. Not uh, not completely right [rewrite]. But expand the while keeping the context similar. Let's say you make it for a vehicle database. Okay, now you are giving a large vehicle like for example, fortune example. Now you." *(incomplete)*
**Interviewee's Answer:** "Yeah." / "Yes."

---



## Question 11

**Question:** "Uh, let's say you are building a chatbot for long conversations. You know, uh, because it's imagine the system is not one shot. You are not going to have 5 or 6 messages, but it will be around, like 100 messages, 200 messages. It can go on 500 messages. There's no limit in that scenario. How will you design a memory around that system, around that? Chatbot specifically?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "So. For larger context, uh, we cannot. We need to have a long term memory. So those memory would go into, if you are specifically talking about chatbot, then the chat messages can be whatever conversation till now has happened. Can go into a SQL database and from. And we can, use that database as long term memory context."

### Counter-Question 11.1

**Question:** "But, uh, in that case, let's say you reach somewhere like 300 messages, right? So 300 messages means 300 user messages, 300 messages. So you end up with 600 messages if you send the entire." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "So if. If the records in database increases, then we will use. We will do normal sharding of the database. So that uh, the load can be handled across various shards of that database."

### Counter-Question 11.2

**Question:** "No, it's not about only sharding. It's about context retention. Let's say the first time I talk to the LLM or you're talking to LM for first 50 messages, we are talking about writing a Python code in 60 messages. You are talking about like porting the Python code to a Java code. And on the next hundred messages you are talking about doing a writing test cases and doing a penetration test. Okay, now let's say the LM still has to know what you talked about, right? How will you manage that memory? Because currently, let's say you are ending up at 300 messages. Now if you keep sending more and more messages, the latency will keep increasing. The next message will take longer time than the previous message." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Okay. So. See, one way is to have a sliding window so that we can get better result. Better result augmented by the the most recent context. Okay, so the backward one will be avoided. The recent ones will be taken into consideration. And the previous one which has which are not within the range of the sliding window. Uh, will become a kind of an episodic memory. And they would be, uh, summarized and, and there would be summarized and would be added on to the, the. Charts which, which came into sliding window range. So sliding window range plus summarized old summarized conversations. They would become the entire chat conversation context."
*AI-assist suggestion present at this point (not spoken by either party).*

#### Sub-Question 11.2.1

**Question:** "So you want to handle the large number of records of the conversation. That is one objective, another objective is to conserve entire context. Or you want to conserve a particular slide [slice] of the context." *(asked by Interviewee)*
**Interviewer's Answer:** "I want to conserve high level context of everything that we have talked about."
**Interviewee's Answer:** No Answer *(Interviewee is the asker)*

### Counter-Question 11.3

**Question:** "And let's say you want to extend this feature and want it to, you know, exist. Between conversations as well. Like let's say you had a 500 long messages today. Next day you start a new message, but you want to refer to this old message. Can you think of any way?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Uh. See? Whenever we whenever we store these conversations, we need to have some metadata which specify that these, these data are associated with that particular user. So, so our agent can be written in such a way that whenever that particular user refers to. I mean, starts a session. Uh. Uh, using. The metadata. Uh, which stores the user name or any user related credential based on that user related credential. We can have the memory fetched of the previous conversation itself."
*AI-assist suggestion present at this point (not spoken by either party).*

#### Sub-Question 11.3.1

**Question:** "You are talking about the context persistence across two chat sessions." *(asked by Interviewee)*
**Interviewer's Answer:** "And not only are close to it can be multiple, it can be 100." and "Yeah."
**Interviewee's Answer:** "Yeah. Multiple chat sessions."

### Counter-Question 11.4

**Question:** "Uh, but okay, you are, but that's just a normal API call. You are just fetching all the previous summary of. Messages that the user had with the. Them and you're using that to enrich it. But that's not a scalable system, right? Let's say the user has 100 conversations over a course of two months. In that case, the won't get just bombarded with old 100 or 200 old chats as a first message itself." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "We will not fetch all of them, only the. Only the only. Those will be retrieved which are semantically matching which our query, which has been asked."
*AI-assist suggestion present at this point (not spoken by either party).*

### Counter-Question 11.5

**Question:** "Okay. And yeah, that's what I'm asking. How will you decide that? Like, how are we going to make that architecture?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "So. So for Agentic flow, I use, a line graph [LangGraph]. To, uh. To make varies across multiple to orchestrate across various agents. So in one of one of the age agents. One of the agents can be assigned for making a tool call to to the databases. And since we have SQL and vector DB, both one one tool can be can be aligned for each of them and and those can be orchestrated using line graph."
*AI-assist suggestion present at this point (not spoken by either party).*

#### Sub-Question 11.5.1

**Question:** "Like. Can you tell me that in detail?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** No Answer *(the Interviewee responds with a clarifying question — see 11.5.2 — and then answers under 11.5)*

#### Sub-Question 11.5.2

**Question:** "There will be. I mean, what you want. You want me to talk about a database? The agent server and the front end." *(asked by Interviewee)*
**Interviewer's Answer:** "And the orchestration, the orchestration." … "Let's say what kind of tools you will have, what kind of databases you will have?" … "What kinds of high level important functions you will have, like, I don't need the full like encryption or entire life cycle. I just want the high level." … "Orchestration and important ones."
**Interviewee's Answer:** "Okay." *(then proceeds with the LangGraph answer recorded under 11.5)*
*AI-assist suggestion present at this point (not spoken by either party).*

### Counter-Question 11.6

**Question:** "And. You will have a tool for memory as well, like summarization." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Yeah. Um, as I told earlier, summarization sliding window plus summarization would happen. So both would be there and both the tools would be one vector DB tool would be using the range for sliding window and the vector DB tool would be after fetch after. Fetching the. The um. After fetch. After fetching the documents. Uh, in that conversation based on metadata, there would be summarized and both would be clubbed together and returned as a. Summed up context. For the LLM to give the response. Okay."
*AI-assist suggestion present at this point (not spoken by either party).*

#### Sub-Question 11.6.1

**Question:** "Sorry, can you repeat that?" *(asked by Interviewee)*
**Interviewer's Answer:** "Uh, one tool call for. Summarizing the conversation that is going out of the rolling summary. You said you will have a rolling window, right? Uh, hot memory and the summary."
**Interviewee's Answer:** No Answer *(Interviewee is the asker; his answer follows under 11.6)*

---



## Question 12

**Question:** "I'll give you one small use case. Uh, I'll put it in the chat. Can you just let me know how you would like? I don't need the full import. I mean, the full pool code level. Or something. But just a high level intuition. Like how would you solve this system?" *(Interviewer 2 — use case shared in chat; the case text itself is not present in the transcript)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "So we need to add an extra layer before the final response is uh. Sent back. And that would validate whether uh, the plan which has been suggested for the customer is too expensive for that customer or not. If it is found to be too expensive, then again, the whole cycle should, uh, again happen. And the. So that."

### Counter-Question 12.1

**Question:** "So the prompt is the user query, right?" *(asked by Interviewee)*
**Interviewer's Answer:** "Uh. I no prompt is the system prompt that we give like it's not a full, highly detailed prompt. It's just an example. Like what is going on? The system prompt."
**Interviewee's Answer:** "Okay." / "Okay."

### Counter-Question 12.2

**Question:** "Whatever is in double quotes is the is the system." *(asked by Interviewee)*
**Interviewer's Answer:** "Yes." … "System prompt. Yes."
**Interviewee's Answer:** No Answer *(Interviewee is the asker)*

### Counter-Question 12.3

**Question:** "And what is that system? Colon." *(asked by Interviewee)*
**Interviewer's Answer:** "Uh, that is the basically like I gave you how the system works. Like basically the high level idea that system uses a vector such and such as like the plan. Based on the user. So basically imagine it, the input is requirements and the output is plans or similar plans. Basically how the system is functioning, right now. And issue is the thing that is being the problem."
**Interviewee's Answer:** No Answer *(Interviewee is the asker)*

### Counter-Question 12.4

**Question:** "So we need to find out on what basis for some users. I mean, what what do you mean by expensive in relation to some user attribute. We need to decide what is expensive, what is not." *(asked by Interviewee)*
**Interviewer's Answer:** "Yes." and "But here expensive can also be compared to, you know, like the needs of the user itself, the user might be asking for something, you know, like, let's say I asked, hey, I want to ask for streaming music. I don't want to use anything else. Just use that mobile data plan. Just to listen to music. And it gave me seven GB per day data, data plan. In that case, it's expensive for me, right? Its a resource which is."
**Interviewee's Answer:** "Prompt is suggesting to maximize the company profit by suggesting the best plan." … "So the best. The word best here might be confusing. The LLM. So. We need to define what is best for the LLM to understand that um."

### Counter-Question 12.5

**Question:** "But in this scenario, what do you think that if you make the system prompt change, it will be a regression risk because the impact. If you see the impact section, it is currently working well for 90% of the other use cases. So if you make any change to the definition of best for them, you might be affecting those 90% of the use cases for the sake of 10%." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Right. So. So we need to add an extra layer before the final response is uh. Sent back. And that would validate whether uh, the plan which has been suggested for the customer is too expensive for that customer or not. If it is found to be too expensive, then again, the whole cycle should, uh, again happen."

### Counter-Question 12.6

**Question:** "So your success. You are. Suggesting a [LLM] as a judge architecture here." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Yes, we have to. Because another agent would be used. And that would be, uh. That would be leveraging another LLM to judge the response of the previous."

### Counter-Question 12.7

**Question:** "Okay. So, uh, I mean, I agree with that thing. But here I want to ask one thing, which basically, yes, you implement law [LLM] as a judge in as an extra layer, what will be the input for that layer? Can you tell me." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "So that. Yeah. So again, um. This LLM judge needs to have a prompt, uh. I mean, the input would be the output, the output which has been given by this previous agent and. That would be used an LLM, llm as a judge would require its own prompt as itself. So what. Yeah. So what. So the prompt for the LLM would say that whatever response has been returned by the previous LLM just read it and. And find out which plan has been extracted for which user. And and then make a and then. We need to use the database for augmenting its. Because as you said. Right. Um. There are can there can be certain plans. Uh. Which can be they can. Be certain plans which can provide the same benefit at a lower price. So we. Need to see what are the, what are, what is the objective of the user from the previous, uh, from the response of the previous LLM. And then match that against. What are the plans which we already have. And among those plans, which are the. Which of them are the cheapest? So this, this should be the prompt for the LLM. So it would become. A rag based."

### Counter-Question 12.8

**Question:** "Yes, I agree to that. But let's say the LM that the first agent, right. The one that gave the initial plan. Also contains the reasoning like why. It gave that plan. Will you pass that reasoning to the judge?" — repeated: "Will you pass that reasoning to the judge? Because you said that you will be passing the prompt rag rag in. In uh, induced context as well as the output of the first agent. Now, let's say first agent. Contains the reasoning as well as the final plan. Will you pass the reasoning and final plan to the. Uh, judge." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Okay, so. Okay, if the reasoning is already there, then." *(incomplete)* … "So we again need to evaluate the reasoning itself. Um."

#### Sub-Question 12.8.1

**Question:** "No. I'm asking, do you want to evaluate the reasoning or not?" *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "See, we need to uh. Whether we need reasoning in that or not. We should, we should need the reasoning because that would only help to evaluate better. Right? Suppose the LLM has provided any reason. However, um, that if we, if we let the reasoning go, then that would again. Uh. Make the LLM as a judge agent, uh, biased towards the. The the target agent itself."

#### Sub-Question 12.8.2

**Question:** "If you pass the reasoning benefit bias, the judge towards the agent right. You should not pass the. Yeah." *(Interviewer 2)*
**Interviewer's Answer:** "Yeah. That is actually true. I think like, uh." and later: "Uh, whenever we are implementing the judge, as long as we are not trying to explicitly judge the reasoning and prompt the judge to only judge the reasoning rather than the output, we should not be passing the reasoning because anytime you pass the reasoning, there is a good chance it will. The second element will just validate the reasoning of how it reached the final generation. Rather than." *(incomplete)*
**Interviewee's Answer:** "Yeah." … "If we pass the agent then it will become biased and would favor the response. If we don't pass it, then it would be neutral." … "Uh, we can avoid the reason. However, we need see, uh, this is very subjective. We need to we need to go through the logs and, and see under what, in what cases, um, the responses are not desirable and what, what, what are the reasons being provided by the, by the LLM I'm talking about the first one. So if we find any correlation that uh, between the two, the reason and the undesired relationship, undesired response, then then we might need to do something about it. Then we may take, we may use reason itself as an indicator that something is wrong with the response. If there is no correlation, which it. Is a kind of a bug for the first LLM. Then we may leave it untouched. We may not pass it into the second LLM as a judge." … Finally: "As I said that that is the more standard way. But uh, see, see, my understanding is that whenever we are building. LLM evaluation, we should go through the logs first and understand what, what are the correlation between the input output and the reason provided by the LLM for that output based on that input. So from there only we can, uh, come up with. A particular kind of. So from there only we can decide what kind of LLM as a judge we want and what prompt should go for that LLM as a judge. However, normally reasons can be avoided to stop. The evaluator from being biased towards the target. LLM."

---



## Question 13

**Question:** "Okay. And let's say I have another question. If you have two models, it's like, okay, not like that. You have both the main worker and the judge, right? Will. Uh, when you're using the judge LLM, will you use a stronger model, a weaker model? By weaker I mean a smaller model or the same model." *(Interviewer 2)*
**Interviewer's Answer:** No Answer
**Interviewee's Answer:** "Yes." … "Generally it would be a stronger model … ll judge." … "Generally."

### Counter-Question 13.1

**Question:** "Can you tell me like, why not a weaker model or. A same model?" *(Interviewer 2)*  
**Interviewer's Answer:** No Answer  
**Interviewee's Answer:** "Evaluating. Right. So, uh, we. Need a stronger reasoning. To do. Evaluation. And that's the reason we should have a stronger model stronger. Model would have would be trained better, would have better reasoning. Uh. So data wise and reasoning wise, both the stronger the, the, the more, uh, the more. Advanced model would be better in those terms. And so we can use that for evaluating in a better way. That's how, that's how generally what happens. However, that still depends upon the use case specific use case, which we are talking about."