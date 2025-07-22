Adding 𝗠𝗖𝗣 to 𝗔𝗴𝗲𝗻𝘁𝗶𝗰 𝗥𝗔𝗚 Systems.

If you are building RAG systems and packing many data sources for retrieval, most likely there is some agency present at least at the data source selection for retrieval stage.

This is how MCP enriches the evolution of your Agentic RAG systems in such case (𝘱𝘰𝘪𝘯𝘵 2.):

𝟭. Analysis of the user query: we pass the original user query to a LLM based Agent for analysis. This is where:

➡️ The original query can be rewritten, sometimes multiple times to create either a single or multiple queries to be passed down the pipeline.
➡️ The agent decides if additional data sources are required to answer the query.

𝟮. If additional data is required, the Retrieval step is triggered. We could tap into variety of data types, few examples:

➡️ Real time user data.
➡️ Internal documents that a user might be interested in.
➡️ Data available on the web.
➡️ …

𝗧𝗵𝗶𝘀 𝗶𝘀 𝘄𝗵𝗲𝗿𝗲 𝗠𝗖𝗣 𝗰𝗼𝗺𝗲𝘀 𝗶𝗻:

✅ Each data domain can manage their own MCP Servers. Exposing specific rules of how the data should be used.
✅ Security and compliance can be ensured on the Servel level for each domain.
✅ New data domains can be easily added to the MCP server pool in a standardised way with no Agent rewrite needed enabling decoupled evolution of the system in terms of 𝗣𝗿𝗼𝗰𝗲𝗱𝘂𝗿𝗮𝗹, 𝗘𝗽𝗶𝘀𝗼𝗱𝗶𝗰 𝗮𝗻𝗱 𝗦𝗲𝗺𝗮𝗻𝘁𝗶𝗰 𝗠𝗲𝗺𝗼𝗿𝘆.
✅ Platform builders can expose their data in a standardised way to external consumers. Enabling easy access to data on the web.
✅ AI Engineers can continue to focus on the topology of the Agent.

𝟯. Retrieved data is consolidated and Reranked by a more powerful model compared to regular embedder. Data points are significantly narrowed down.
𝟰. If there is no need for additional data, we try to compose the answer (or multiple answers or a set of actions) straight via an LLM.
𝟱. The answer gets analyzed, summarized and evaluated for correctness and relevance:

➡️ If the Agent decides that the answer is good enough, it gets returned to the user.
➡️ If the Agent decides that the answer needs improvement, we try to rewrite the user query and repeat the generation loop.



[text](AgenticRAG.md)