# Query Mate: Chat With Your Database

**TL, DR:** A Secure Retrieval-Augmented Text-to-SQL System for Large Relational Databases.

The goal is to develop an intelligent database querying system that enables users (most especially, non-technical users - for instance, stakeholders) to interact with their relational databases using natural language instead of SQL syntax. The system capitalizes on the impressive capabilities of Large Language Models (LLMs) to translate user questions into SQL queries and format database responses in human-readable language. Handling of databases with a large number of tables, and security concerns or measures about database credentials are enforced and highly considered in this project implementation.


## Core Functionality
The system provides a natural language interface for querying relational databases through the following workflow: 
- Database Connection: Users establish a read-only connection to their database.
- Natural Language Input: Users submit questions in plain english.
- SQL Translation: The LLM converts the natural language question into a valid SQL query.
- Query Execution: The generated SQL query retrieves requested information from the database 
- Response Generation: The LLM transforms the database results into a natural language response 
- User Display: The formatted answer is presented to the user through a web interface

## Supported Databases 
Currently, it only provides support for three relational database management systems (RDBMS). They are:
- PostgreSQL 
- SQLite 
- MySQL


## Key Components 
- LLM Integration: Natural language processing for query translation and response generation 
- Database Schema Understanding: Object-Relational Mapping (ORM) to enable the LLM to comprehend database structure, relationships, and constraints 
- SQL Agent: Intelligent agent for query generation and validation 
- Web User Interface: Browser-based interface for user interaction 
- Read-Only Access Control: Security enforcement to prevent data modification 

## System Architecture 
This system operates or functions as an AI-assisted database agent that: 
- Maintains comprehensive knowledge of the connected database schema through ORM
- Translates natural language to SQL with contextual understanding 
- Executes queries safely with read-only permissions 
- Provides human-friendly explanations of query results 

## Use Cases 
- Non-technical users (Stakeholders) querying databases without SQL knowledge 
- Rapid data exploration and analysis 
- Business intelligence and reporting through conversational interface 
- Database documentation and understanding through natural language queries 

## Security Considerations 

- Enforced read-only database access 
- Query validation before execution 
- No data modification capabilities 
- Secure database credential handling: Ensure that database credentials are collected securely.

