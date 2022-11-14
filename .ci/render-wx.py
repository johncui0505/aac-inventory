# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Daniel Schmidt <danischm@cisco.com>

import os
import re

TEMPLATE = """[**[{{ build.status }}] {{ repo.owner }}/{{ repo.name }} #{{ build.number }}**]({{ build.link }})
* Commit: [{{ commit.message }}]({{ commit.link }})
* Author: {{ commit.author.name }} {{ commit.author.email }}
* Branch: {{ commit.branch }}
* Event: {{ build.event }}
* Started at: {{ datetime build.created "Mon Jan 2 15:04:05 MST 2006" "Local" }}
"""

VALIDATE_OUTPUT = """\n**Validation Errors**
```
"""

RENDER_OUTPUT = """\n**Render Summary**
```
"""

NAE_OUTPUT = """\n[**NAE Pre-Change Validation**](https://10.51.77.57)
```
"""

DEPLOY_OUTPUT = """\n[**Deploy Summary**](https://10.50.223.165/aci-iac/aac-inventory/commit/master)
```
"""

TEST_OUTPUT = """\n**Test Summary** [**APIC**](https://engci-maven-master.cisco.com/artifactory/list/AS-release/Community/aac-inventory/{{ build.number }}/test_results/lab/apic1/log.html) [**MSO**](https://engci-maven-master.cisco.com/artifactory/list/AS-release/Community/aac-inventory/{{ build.number }}/test_results/lab/mso1/log.html)
```
"""


def parse_ansible_errors(filename):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    lines = ""
    if os.path.isfile(filename):
        with open(filename, "r") as file:
            output = file.read()
            output = ansi_escape.sub("", output)
            add_lines = False
            for index, line in enumerate(output.split("\n")):
                if add_lines:
                    if len(line.strip()):
                        lines += line + "\n"
                    else:
                        add_lines = False
                if line.startswith("fatal:"):
                    lines += output.split("\n")[index - 1] + "\n"
                    lines += line + "\n"
                    add_lines = True
    return lines


def parse_ansible_summary(filename):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    lines = ""
    if os.path.isfile(filename):
        with open(filename, "r") as file:
            output = file.read()
            output = ansi_escape.sub("", output)
            add_lines = False
            for index, line in enumerate(output.split("\n")):
                if add_lines:
                    if len(line.strip()):
                        lines += line + "\n"
                    else:
                        add_lines = False
                if line.startswith("PLAY RECAP"):
                    lines += line + "\n"
                    add_lines = True
    return lines


if __name__ == "__main__":
    validate_lines = parse_ansible_errors("./validate_output.txt")
    render_lines = parse_ansible_summary("./render_output.txt")
    nae_lines = parse_ansible_errors("./nae_output.txt")
    deploy_lines = parse_ansible_summary("./deploy_output.txt")
    test_lines = parse_ansible_summary("./test_output.txt")

    if validate_lines:
        validate_lines = VALIDATE_OUTPUT + validate_lines + "\n```\n"
    if render_lines:
        render_lines = RENDER_OUTPUT + render_lines + "\n```\n"
    if nae_lines:
        nae_lines = NAE_OUTPUT + nae_lines + "\n```\n"
    if deploy_lines:
        deploy_lines = DEPLOY_OUTPUT + deploy_lines + "\n```\n"
    if test_lines:
        test_lines = TEST_OUTPUT + test_lines + "\n```\n"
    with open("./webex.txt", "w") as out_file:
        out_file.write(TEMPLATE)
        if validate_lines:
            out_file.write(validate_lines)
        if render_lines:
            out_file.write(render_lines)
        if nae_lines:
            out_file.write(nae_lines)
        if deploy_lines:
            out_file.write(deploy_lines)
        if test_lines:
            out_file.write(test_lines)
