# CertStream User Guide

Welcome to CertStream! Choose a section from the table of contents below to find step-by-step guides on how to use CertStream.

> 💡 Updates: Google Colab version out [here](https://colab.research.google.com/drive/1GxTKUsq54Xt9mdvqI7q-C9oT383PRoCh?usp=sharing).

--------------------------------------------------------------------------------------------------------------------

## Table of Contents

1. [Introduction to CertStream](#introduction-to-certstream)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
3. [Feedback](#feedback)
4. [Authors](#authors)

--------------------------------------------------------------------------------------------------------------------

## Introduction to CertStream

CertStream is an easy-to-deploy Python Script designed for Cybersecurity Researchers. It seamlessly captures newly-registered domains that matches your capture regexes.

The CertStream User Guide acquaints you with the application's functionality, enabling you to maximize its potential.

Key Features:

* Retrieve domains from Certificate Transparency's vast network of monitors.
* Filters for domains of interest with one or more capture regexes.
* Stores domains of interest into a SQLite database.

> 💡 CertStream only requires one command to start. CertStream is user-friendly!

We are confident that CertStream will enhance your efficiency as Cybersecurity Researchers. Enjoy your experience with CertStream! :)

--------------------------------------------------------------------------------------------------------------------

## Quick Start

1. Download `CertStream.zip` [here](https://github.com/choonyongchan/CertStream/releases/download/v1.0/CertStream.zip), and extract `CertStream.zip` to any folder.

<img src="docs/images/quickstart0.png" alt="quickstart0" width="400"/>

2. Open the `/input` folder, and edit `input_regex.txt` using any text editor.

<img src="docs/images/quickstart1.png" alt="quickstart" width="400"/>

3. Add one or more regexes for CertStream to monitor, and save the file. 

    CertStream will capture domains that matches any of the regexes.

    (e.g. The domain `google123.com` will be captured using the regexes below.)

<img src="docs/images/quickstart2.png" alt="quickstart2" width="400"/>

4. Navigate back to the previous folder.

<img src="docs/images/quickstart0.png" alt="quickstart0" width="400"/>

5. Open Command Prompt/Terminal on the home folder. For Windows users, follow the instructions below.

    1. Click on the address bar.

    <img src="docs/images/quickstart3.png" alt="quickstart3" width="400"/>

    3. Type `cmd`, and press `Enter` to launch Command Prompt.

    <img src="docs/images/quickstart4.png" alt="quickstart4" width="400"/>

6. Copy each command below, and press `Enter` to start CertStream. 

```
python -m pip install -r src/requirements.txt
python Main.py
```
<img src="docs/images/quickstart5.png" alt="quickstart5" width="400"/>

> 💡 If the above command throws an error, try replacing `python` with `python3`.

7. To stop CertStream, press CTRL+C (You may need to press a few times). 

    Domains captured is exported to an output file.

> 💡 More time is needed for export when the number of domains stored is large.

<img src="docs/images/quickstart6.png" alt="quickstart6" width="400"/>

8. Open the new `/logs` folder. 

<img src="docs/images/quickstart9.png" alt="quickstart9" width="400"/>

   You will find the `CertStream.txt` output file.

9. Open `CertStream.txt` to view the captured domains. 

<img src="docs/images/quickstart8.png" alt="quickstart8" width="400"/>


--------------------------------------------------------------------------------------------------------------------

## Configuration

You can customise CertStream's configuration to suit your workflow.

1. Open the `/input` folder, and edit `config.yaml` using any text editor.

<img src="docs/images/config1.png" alt="config1" width="400"/>

2. You may customise the input/output filenames and other settings. Save the file.

<img src="docs/images/config2.png" alt="config2" width="400"/>

3. Run CertStream as usual. Refer to [Quick Start Step 4](#quick-start).

--------------------------------------------------------------------------------------------------------------------

## Feedback

CertStream is a pilot program. Any feedback is appreciated while we develop CertStream. To deposit ideas and comments, create a new Issue on Github!

--------------------------------------------------------------------------------------------------------------------

## Authors

This User Guide is written by [Choon Yong](https://github.com/choonyongchan).