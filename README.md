# GPT Developer

This is a GitHub Action that asks GPT to edit your code for you.

## Quick Start

1. Go to the project template: https://github.com/skaramicke/gpt-developer-project-template
2. Click the `Use this template` button
3. Create a new repository from the template
4. Add your OpenAI API key as a secret to the repository with the name `OPENAI_API_SECRET`
5. Create an issue with the label `gpt-developer` and the action will run and update the code according to the title and description of the issue.

## Inputs

`openai_api_key`  
**Required** Your OpenAI API key. You can get one from https://beta.openai.com/account/api-keys.

`issue_number`  
**Required** The number of the issue to comment on.

`issue_text`  
**Required** The text to run through GPT.

## Outputs

`comment_message`  
If the AI decides it can't do anything with the issue text, it will issue an exit message and stop the process.

`commit_message`  
When the AI is done with the code, it will commit the changes with this commit message.

A closing statement for the issue number is added no matter what the AI decides to write.

## Example usage

1. Create a github workflow `.github/workflows/gpt-developer.yml`:

```yaml
name: GPT Developer

on:
  issues:
    types:
      - labeled

jobs:
  update-code-on-issue:
    if: github.event.label.name == 'gpt-developer'
    name: Update the code according to issue text
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: write
    steps:
      - uses: ben-z/actions-comment-on-issue@1.0.2
        with:
          message: "I'm working on it! - GPT Developer"
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Checkout code
        uses: actions/checkout@v2

      - name: Update code
        uses: skaramicke/gpt-developer@v1
        id: gpt
        with:
          openai_api_key: ${{ secrets.OPENAI_API_SECRET }}
          issue_number: ${{ github.event.issue.number }}
          issue_text: "${{ github.event.issue.title}}, ${{ github.event.issue.body }} - created by ${{ github.event.issue.user.login }}"
          path: ${{ github.workspace }}

      - uses: ben-z/actions-comment-on-issue@1.0.2
        if: ${{ steps.gpt.outputs.comment_message != '' }}
        with:
          message: ${{ steps.gpt.outputs.comment_message }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Commit changes
        if: ${{ steps.gpt.outputs.commit_message != '' }}
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: ${{ steps.gpt.outputs.commit_message }} - gpt-developer

      - uses: ben-z/actions-comment-on-issue@1.0.2
        if: ${{ steps.gpt.outputs.commit_message != '' }}
        with:
          message: 'I''ve updated the code with this commit message: "${{ steps.gpt.outputs.commit_message }}" - GPT Developer'
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

2. Create an issue with the label `gpt-developer` and the action will run and update the code according to the title and description of the issue.
3. ???
4. Profit!!1
