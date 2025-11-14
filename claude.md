The goal is to showcase that we can automatically extract data from a sqlite database hosted locally, and from this sqlite, we have an LLM, fill in the pdf field: /Users/philippebeliveau/Desktop/Notebook/EZBI/proxima/Proxima/2025-02-13 KIT Marc-Olivier - COMPLET.pdf

We are a small consulting firm showcasing to this business that we can automatize much of their operations: /Users/philippebeliveau/Desktop/Notebook/EZBI/proxima/Proxima/proxima-info.md

First, we need to: 
1. Create an sqlite database in: /Users/philippebeliveau/Desktop/Notebook/EZBI/proxima/Proxima/data/sqlite
2. You need to read the file: /Users/philippebeliveau/Desktop/Notebook/EZBI/proxima/Proxima/2025-02-13 KIT Marc-Olivier - COMPLET.pdf
3. Extract all the fields
4. Populate the sqlite database with all the fields it would be need to populate this pdf. 
5. Create 20 synthetic records of clients like that 
6. Have an LLM from open router (see .env.local, the key is there with deepkseek model) going into the db,  extracting the fields
7. From these extracted fields, populate the pdf
8. Put all the populated pdf in here; /Users/philippebeliveau/Desktop/Notebook/EZBI/proxima/Proxima/data/populated-pdf

* the pipeline needs to be quick, efficient, its a demo. Dont overcomplicate, solve this alone. 