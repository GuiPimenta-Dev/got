from abc import ABC, abstractmethod


class AI(ABC):
    examples = open("got/prompts/examples.txt", "r").read()
    
    @abstractmethod
    def prompt(self, prompt: str) -> str:
        pass

    @abstractmethod
    def add_message(self, content: str, role: str = "user") -> None:
        pass

    @property
    def commit_suffix(self) -> str:
        suffix = f"""
If two or more files have related changes, please merge them together in one single commit!

Here is the format in which I will send you the file details:
  ```json
  {{
    "file_path": "example/path",
    "previous_commit": "previous commit file content, if there is some"
    "commit": "current commit file content",
    "diff": "diff from current content from previous, if there is some"
  }}
  ```
Please focus primarily on the `commit` key as it reflects the current changes being made. The `previous_commit` and `diff` keys are provided to give context and help you understand the progression of the changes.

Your response should also be in JSON format, containing a list of file groups with their associated commit messages. Here’s how the response should be structured:

{{
    "commits": [
      {{
        "files": [
          "path/to/file1",
          "path/to/file2"
        ],
        "messages": {self.examples}
      }},
      {{
        "files": [
          "path/to/file3"
        ],
        "messages": {self.examples}
      }}
    ]
  }}
"""
        return suffix

    @property
    def retry_suffix(self) -> str:
        return f"""
Here is the format in which I will send you the file details:

 ```json
  {{
    "file_path": "example/path",
    "previous_commit": "previous commit file content, if there is some"
    "commit": "current commit file content",
    "diff": "diff from current content from previous, if there is some"
  }}
```
Please focus primarily on the `commit` key as it reflects the current changes being made. The `previous_commit` and `diff` keys are provided to give context and help you understand the progression of the changes.

The response should also be in JSON format, structured as follows: 
{
  "messages": {self.examples}
}
"""
