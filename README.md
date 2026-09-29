# Homelessness Data Analysis

This repository contains exploratory data analysis and visualization work focused on homelessness data, including a geographic analysis of Koreatown in Los Angeles.

The project uses Python, R, Jupyter Notebooks, and R Markdown to clean data, investigate patterns, and communicate findings through visualizations.

## Repository Structure

```text
homelessness_dataset/
├── data/                    # Raw and/or processed datasets
├── figures/                 # Generated plots, maps, and visualizations
├── analysis.ipynb           # Primary exploratory analysis notebook
├── analysis_1.ipynb         # Additional Jupyter Notebook analysis
├── analysis_1.rmd           # R Markdown analysis and report
├── koreatown_analysis.py    # Python analysis focused on Koreatown
└── README.md
```

## Project Goals

This project aims to:

- Explore patterns in homelessness-related data.
- Clean and prepare datasets for analysis.
- Examine geographic and demographic trends.
- Analyze homelessness data relevant to Koreatown.
- Create clear visualizations that support data-driven interpretation.
- Practice reproducible analysis workflows using Python and R.

## Tools and Technologies

- **Python**
  - pandas
  - NumPy
  - matplotlib
  - seaborn
  - Jupyter Notebook

- **R**
  - R Markdown
  - tidyverse packages, where applicable
  - Data visualization and statistical analysis tools

## Getting Started

### 1. Clone the repository

```bash
git clone [https://github.com/rxqnx00/homelessness_dataset.git](https://github.com/rxqnx00/homelessness_dataset.git)
cd homelessness_dataset
```

### 2. Set up Python

Create and activate a virtual environment:

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install commonly used Python packages:

```bash
pip install pandas numpy matplotlib seaborn jupyter
```

### 3. Launch the notebooks

```bash
jupyter notebook
```

Then open either `analysis.ipynb` or `analysis_1.ipynb` in your browser.

### 4. Run the Python script

```bash
python koreatown_analysis.py
```

### 5. Render the R Markdown report

Open `analysis_1.rmd` in RStudio and select **Knit**, or run:

```r
rmarkdown::render("analysis_1.rmd")
```

## Data

Place datasets used in the project inside the `data/` directory.

To keep the project reproducible, document the following for each dataset:

- Source or organization that published the data
- Download date
- Geographic coverage
- Relevant time period
- Important cleaning or preprocessing steps
- Licensing or usage restrictions

> Do not upload sensitive, personally identifiable, or restricted data to this public repository.

## Outputs

Visualizations and other generated outputs should be saved in the `figures/` directory. Examples may include:

- Bar charts and trend plots
- Geographic maps
- Distribution plots
- Correlation or comparison graphics
- Summary tables exported from the analysis

## Reproducibility Notes

- Run the notebooks and scripts from the repository root directory.
- Keep raw data separate from cleaned or derived data when possible.
- Record package versions if the analysis is expanded into a formal report.
- Add a `requirements.txt` file for Python dependencies and, if needed, a package list for R.

## Future Improvements

- Add a detailed data dictionary.
- Document the exact data source(s) and collection methodology.
- Add a `requirements.txt` file.
- Add an interactive map or dashboard.
- Expand comparisons across Los Angeles neighborhoods.
- Add tests or validation checks for data-cleaning steps.
- Publish a final written report with key findings.

## Author

Ryan Yoo  
UCLA Statistics and Data Science Student

## License

This project is intended for educational and portfolio purposes. Add a license file, such as the MIT License, if you would like others to reuse or adapt the code.
