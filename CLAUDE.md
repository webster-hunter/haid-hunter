# hAId-hunter

NOTE: All design decisions made here are superseded by the specs in the docs/superpowers/specs directory

The purpose of this application is to build a highly optimized job application experience for the current landscape of AI-driven hiring. The primary means of approaching this issue is to identify the key language in targeted job postings and the relevant experience of the user to give them a true chance to let their story speak for them.

## Components

- Locally hosted task tracking application accessed via web-browser
    - I really cannot be bothered to set up and pay for cloud resources, so this application will be accessible from a local server.
    - Phase I Plans:
        - The application will be a task tracker akin to Jira. I want the user to be able to develop "documentation" on themselves that can be used to as a knowledge base for agents to reference when tailoring resumes and cover lettters. The idea is to be able to tailor your story to the job posting in the little space provided to do so.
    - Phase II Plans:
        - The application will be able to use temporary emails and applicant accounts to track the status of job applications.
    - Phase III Plans:
        - The application will be able to submit the information directly into the listing

## Tech Stack
- Dev Server: Vite
- Front End: React
- Backend: Python
- Scripting: TypeScript

## Home Page
- The home page will have 3 primary functionalities and be developed as a React SPA:
    
    - Document Management: Add, remove, and view all of the documents that will be used as a knowledge base for your job seeker profile
        - For simplicity, documents will be tracked by placing them in a directory, with sub-directories for each document type (resume, cover letter, cv, user defined tags, etc.)
    - Profile View: A breakdown of all of your candidate profile -- skills, experience, goals. Claude will generate suggestions to add, but the user can refine them as necessary
        - Candidate profile information will be stored as a json doc in the documents directory
    - Application Manager: Create, view, and track the state of all of the postings you are pursuing.
        - Stored in a PostgreSQL database
            - Schema: id (int), Company (string), Position (string), Posting URL (string), Candidate Login Page (string), login (string, encrpted using Python's encryption library w/ key in .env), application status (string)
        - Button to update the status of the applications that are pending (either claude agent-browser, wget, or something else)
    - Next Steps (Phase II): Claude-driven suggestions about what you should do to make yourself more appealing based off of your documents and applications.
    - Seeker (Phase III): Define a set of locations and remote/on-site preferences and have claude search for recent postings tailored to you (1 day/1 week/1 month)


