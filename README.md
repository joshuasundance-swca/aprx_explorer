# aprx_explorer

## Requirements

* `beautifulsoup4`
* `pandas`
* `pydantic`

## Optional (for summaries)

* `langchain`
  - `langchain_community`
  - `langchain_core`
  - `langchain_openai`
* `openai`

## Installation

```bash
git clone https://github.com/joshuasundance-swca/aprx_explorer.git
cd aprx_explorer
pip install .

# or to install optional dependencies for summarization:
# pip install .[summarize]
```

## Usage

### See Help
```bash
usage: aprx_explorer [-h] [--openai_api_key OPENAI_API_KEY] [--model MODEL] [--summarize] aprx output

Extract geoprocessing history objects from an ArcGIS Pro project file.

positional arguments:
  aprx                  Path to an ArcGIS Pro project file.
  output                Path to save the output CSV or Parquet file.

options:
  -h, --help            show this help message and exit
  --openai_api_key OPENAI_API_KEY
                        Omit for a secure prompt
  --model MODEL         Default: gpt-4-0125-preview
  --summarize           Summarize the geoprocessing history objects.
```
