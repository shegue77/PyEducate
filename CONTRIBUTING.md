# Contributing to PyEducate

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. See the [Table of Contents](#table-of-contents) for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution. It will make it a lot easier for us maintainers and smooth out the experience for all involved. The community looks forward to your contributions. 🎉

> And if you like the project, but just don't have time to contribute, that's fine. There are other easy ways to support the project and show your **appreciation**, which we would also be very happy about:
> - Star the project ⭐
> - Tweet about it
> - Refer this project in your project's readme
> - Mention the project at local meetups and tell your friends/colleagues 📢

<!-- omit in toc -->
## Table of Contents

- [I Have a Question](#i-have-a-question)
- [I Want To Contribute](#i-want-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements & New Features](#suggesting-enhancements)
- [What To Contribute](#what-to-contribute)

## I Have a Question

Before you ask a question, it is best to search for existing [Issues](https://github.com/shegue77/PyEducate/issues) that might help you. In case you have found a suitable issue and still need clarification, you can write your question in this issue. It is also advisable to search the internet for answers first.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [Issue](https://github.com/shegue77/PyEducate/issues/new).
- Provide as much context as you can about what you're running into.
- Provide project and platform versions, depending on what seems relevant.

We will then take care of the issue as soon as possible.

<!--
You might want to create a separate issue tag for questions and include it in this description. People should then tag their issues accordingly.

Depending on how large the project is, you may want to outsource the questioning, e.g. to Stack Overflow or Gitter. You may add additional contact and information possibilities:
- IRC
- Slack
- Gitter
- Stack Overflow tag
- Blog
- FAQ
- Roadmap
- E-Mail List
- Forum
-->

## I Want To Contribute

### Submitting a PR

---
### **Contributor License Agreement (CLA)**

Before contributing code to PyEducate, you must sign our [Contributor License Agreement (CLA)](https://cla-assistant.io/shegue77/PyEducate). This is a legal requirement for all contributions to be merged into the main repository.

**Important:** We strongly recommend reviewing and signing the CLA before starting work on your contribution to avoid any delays in the PR process.

---

### 1. Setup Your Local Development Environment

```bash
# Clone the repository
git clone https://github.com/shegue77/PyEducate.git
cd PyEducate

# Create new branch
git checkout -b your-feature-branch

# Install dependencies
pip install -r requirements.txt
```

That's it! Your local development environment is ready.

### 2. Development Workflow

Here's the recommended workflow for making changes:

```bash
# Make your changes to the code
# ...

# Commit your changes
git add .
git commit -m "Your descriptive commit message"

# Push and create a PR
git push origin your-feature-branch
```

### Reporting Bugs

#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Therefore, we ask you to investigate carefully, collect information and describe the issue in detail in your report. Please complete the following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side e.g. using incompatible environment components/versions (If you are looking for support, you might want to check [this section](#i-have-a-question)).
- To see if other users have experienced (and potentially already solved) the same issue you are having, check if there is not already a bug report existing for your bug or error in the [bug tracker](https://github.com/shegue77/PyEducate/issues?q=label%3Abug).
- Also make sure to search the internet (including Stack Overflow) to see if users outside of the GitHub community have discussed the issue.
- Collect information about the bug:
- OS, Platform and Version (Windows, Linux, macOS, x86, ARM)
- Version of the interpreter, runtime environment, package manager, depending on what seems relevant.
- Possibly your input and the output
- Can you reliably reproduce the issue? And can you also reproduce it with older versions?

#### How Do I Submit a Good Bug Report?

> You must never report security related issues, vulnerabilities or bugs including sensitive information to the issue tracker, or elsewhere in public. Instead sensitive bugs must be sent via Github's [Security](https://github.com/shegue77/PyEducate/security) feature.

We use GitHub issues to track bugs and errors. If you run into an issue with the project:

- Open an [Issue](https://github.com/shegue77/PyEducate/issues/new). (Since we can't be sure at this point whether it is a bug or not, we ask you not to talk about a bug yet and not to label the issue.)
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the *reproduction steps* that someone else can follow to recreate the issue on their own. This usually includes your code. For good bug reports you should isolate the problem and create a reduced test case.
- Provide the information you collected in the previous section.

Once it's filed:

- The project team will label the issue accordingly.
- A team member will try to reproduce the issue with your provided steps. If there are no reproduction steps or no obvious way to reproduce the issue, the team will ask you for those steps and mark the issue as `needs-repro`. Bugs with the `needs-repro` tag will not be addressed until they are reproduced.
- If the team is able to reproduce the issue, it will be marked `needs-fix`, as well as possibly other tags (such as `critical`), and the issue will be left to be implemented by someone.


### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for PyEducate, **including completely new features and minor improvements to existing functionality**. Following these guidelines will help maintainers and the community to understand your suggestion and find related suggestions.

#### Before Submitting an Enhancement
<!-- omit in toc -->

- Make sure that you are using the latest version.
- Perform a [search](https://github.com/shegue77/PyEducate/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to you to make a strong case to convince the project's developers of the merits of this feature. Keep in mind that we want features that will be useful to the majority of our users and not just a small subset. If you're just targeting a minority of users, consider writing an add-on/plugin library.

#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://github.com/shegue77/PyEducate/issues).

- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why. At this point you can also tell which alternatives do not work for you.
- You may want to **include screenshots or screen recordings** which help you demonstrate the steps or point out the part which the suggestion is related to.
- **Explain why this enhancement would be useful** to most PyEducate users. You may also want to point out the other projects that solved it better and which could serve as inspiration.

## What to Contribute

Looking for ideas? Check out:

- 🐛 [Good first issues](https://github.com/shegue77/PyEducate/labels/good%20first%20issue)
- 🚀 [Feature requests](https://github.com/shegue77/PyEducate/labels/enhancement)
- 🧪 Test coverage improvements

Thank you for contributing to PyEducate! 🚀 