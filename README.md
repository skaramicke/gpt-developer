# GPT Developer

This is a GitHub Action that asks GPT to edit your code for you.

## Inputs

### `openai_api_key`

**Required** Your OpenAI API key. You can get one from https://beta.openai.com/account/api-keys.

### `issue_number`

**Required** The number of the issue to comment on.

### `issue_text`

**Required** The text to run through GPT.

## Outputs

## Example usage

```
name: GPT Developer

on:
  issues:
    types: [opened]

env:
  CODE_PATH: code

jobs:
  update-code-on-issue:
    name: Update the code according to issue text
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v2
      with:
        path: ${{ env.CODE_PATH }}

    - name: Update code
      uses: skaramicke/gpt-developer@v1
      id: gpt
      with:
        openai_api_key: ${{ secrets.OPENAI_API_KEY }}
        issue_number: ${{ github.event.issue.number }}
        issue_text: "${{ github.event.issue.title}}, ${{ github.event.issue.body }}"
        path: ${{ env.CODE_PATH }}

    - name: Commit changes
      uses: EndBug/add-and-commit@v7
      with:
        author_name: GPT Developer
        commit_message: ${{ steps.gpt.outputs.commit_message }}
```
