# <p align="center">New is always better</p>

<p align="center">
    <img src="welcome_page.png" alt="Welcome" >
</p>

New is always better is an independent cinema with a unique policy: it exclusively screens new movie releases, rotating its program weekly with one new film per screen (120 and 80 seats respectively). The current film selection relies on the manager’s industry monitoring, festival attendance (e.g., Cannes, Deauville), and intuition—an effective but time-consuming approach.

To streamline this process, the cinema seeks to develop an AI-powered decision-making tool that predicts the attendance of new movie releases during their first week. This tool aims to support programming decisions by identifying which films are likely to attract the most viewers, thus optimizing audience engagement and revenue. The final solution should be accessible via a simple web or mobile application, requiring no technical knowledge from the user.

## ➔ Table of Contents



* [➔ Context](#-context)
* [➔ Team and Workflow](#-team-and-workflow)
* [➔ Description](#-description)
* [➔ Project Structure](#-project-structure)
* [➔ How to Run](#-how-to-run)
* [➔ Requirements](#-requirements)
* [➔ Evaluation Criteria](#-evaluation-criteria)
* [➔ License](#-license)
* [➔ Authors](#-authors)

---
## Context
This project is part of a training program and allows the team to apply all the skills they have acquired throughout the course: core programming languages (**Python** and **SQL**), machine learning models (**linear regressions**, **XGBoost**, **lightGBM**), API development with **FastAPI**, web development with **Django**, and deployment on a cloud platform (**Azure**).

---
## Team and Workflow
The team is a squad of **4 full-stack data/AI developers in training**. The squad follows the **Agile methodology**, and the work was carried out over one month, divided into **four 7-day sprints**.

- **Sprint 1** : focused on defining the project scope, drafting the functional specifications, and estimating the costs.

- **Sprint 2**: involved web scraping, data cleaning and analysis, and the development of the first machine learning models.

- **Sprint 3**: was dedicated to building the first version of the application.

- **Sprint 4**: focused on deploying a fully functional version of the application.

Each sprint began with a **sprint planning meeting** to define the backlog, select user stories, and assign tickets. A **daily stand-up meeting**, led by the **Scrum Master**, was held every morning. At the end of each sprint, a **sprint review** was conducted by the **Product Owner** with the client, followed by a **sprint retrospective** to review and improve the process.

## Project Structure

This project includes the following main files and modules:

- **new_is_always_better/**
    - **api/**  
        - **app/** 
            - **utils/**: Utility files and functions.
            - **main.py**: Entry point for the API.
            - **predict.py**: Machine learning model for the prediction of movies success.
            - **schemas.py**: Defines the model of datas needed for predictions.
    - **django/**
        - **NewIsAlwaysBetter/**
            - **app/**
            - **NewIsAlwaysBetter/**
            - **static/**
            - **staticfiles/**
            - **templates/**
            - **theme/**
            - **manage.py**
    - **modelisation/**
        - **ludi/** Contains notebooks with linear models and the analysis of datas.
        - **victor/** Contains notebooks with boosted models, the best model and the features engineering.
    - **scrapping/**
        - **airflow/**
            - **dags/**
                - **scraping_dag.py** Automates the allocine_spider_releases.py execution once a week.
        - **allocine_scrapping/**
            - **allocine_scrapping/**
            - **scrapping/**: Contains logs.
            - **spiders/**
                - **allocine_spider_releases.py**: Gets the last release of movies.
                - **allocine_spider.py**: Gets all the movies and informations about movies released during a defined period.
            - **pipelines.py** : Defines datas processings, storage, calls the API for predictions and stores the results.
            - **runner_releases.py**: Entry point for the allocine_spider_releases.py spider.
            - **runner.py**: Entry point for the allocine_spide.py spider.
        - **cnc_scraper/**
            - **cnc_data/**: Contains all the datas
            - **cnc_scraper/**
                - **spiders/**
                    - **cnc.py** Gets informations about cinema frequentations in France.
                - **pipelines.py** Stores the datas into a parquet file.
        - **ecrantotal_scraper/**
            - **ecrantotal_scraper/**
                - **spiders/**
                    - **ecrantotal_spiders.py** Gets movies scheduled for release in the next three years.
                - **pipelines.py** Stores the datas into a parquet file.
        - **imdb_scraper/**
            - **imdb_scraper/**
                - **spiders/**
                    **imbd_spider.py** Retrieves movies datas from imdb website
                - **pipeline.py** Processes the datas and stores it in parquet file.
        - **jpboxoffice/**
            - **jpboxoffice/**
                - **spiders/**
                    - **jpboxoffice_spider.py** Retrieves the top actors based on their number of ticket sales in France.
        - **plugins/**
        - **deploy.sh** : Allows to deploy the weekly scraping on Azure platform.


---

<!-- ## How to Run

Follow these steps to run the project:

1. Ensure Python >= 3.9 is installed on your system.
2. Clone this repository to your local machine:

```bash
    git clone https://github.com/Daviddavid-sudo/Gestion-des-Performances-des-Cyclistes-Professionnels.git
```
3. Navigate to the project directory:

```bash
    cd Gestion-des-Performances-des-Cyclistes-Professionnels
```
4. Install the required dependencies:

```bash
    pip install -r requirements.txt
```
5. Fill the database :

```bash
    python Fill_athlete_user_table.py
```
5. (bis, Optional) Add some Performances Datas:

```bash
    python fill_athlete_user_table.py
```
6. Run the FastAPI application:

```bash
    uvicorn app.main:app --reload
```
7. In an new terminal, navigate to the project directory:

```bash
    cd ..
    cd streamlit
```
8. Run the Streamlit application

```bash
    streamlit run app.py
```
---

## Requirements

List of required software and libraries:

- Python >= 3.9
- fastapi
- streamlit
- passlib
- uvicorn
- dotenv
- jose
- jwt
- bcrypt
- python-jose
- email-validator

--- -->

## Evaluation Criteria

### Educational Requirements
- Group of 4 members
- Duration: 1 months


### Deliverables
- Link to the GitHub repository
- Oral presentation including testing

---

## Performance Metrics

- The application and API meet the project requirements.
- No obvious security vulnerabilities.

---

## License

[MIT License](LICENSE)

---

## Authors

- **David Scott**
  <a href="https://github.com/Daviddavid-sudo" target="_blank">
      <img loading="lazy" src="images/github-mark.png" width="30" height="30" alt="GitHub Logo">
  </a>

- **Ludivine Raby**
  <a href="https://github.com/ludivineRB" target="_blank">
      <img loading="lazy" src="images/github-mark.png" width="30" height="30" alt="GitHub Logo">
  </a>

---