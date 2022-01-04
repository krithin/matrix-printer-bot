# Matrix Printer Bot [![Built with matrix-nio](https://img.shields.io/badge/built%20with-matrix--nio-brightgreen)](https://github.com/poljar/matrix-nio) <a href="https://matrix.to/#/#nio-template:matrix.org"><img src="https://img.shields.io/matrix/nio-template:matrix.org?color=blue&label=Join%20the%20Matrix%20Room&server_fqdn=matrix-client.matrix.org" /></a>

A Matrix bot that prints PDFs sent to it.

Requires a local printer to already be set up through CUPS. Because this currently execs off an `lp` command instaed of doing anything fancy with the CUPS API, this bot must be run directly on the machine that has printer access, and cannot be run through Docker.

Because this does stuff in the physical world I've limited this bot to only accept room invites from people who have accounts on the same homeserver as the bot. This works well for me because I run my own Matrix homeserver with public registration disabled. You might have to evaluate your own approach to security when using this bot.

## Installation

### Systemwide stuff
1. Install `libolm`. I had to [build this from source](https://gitlab.matrix.org/matrix-org/olm#building) and then install it by hand (with a `sudo make install`) because of some incompatibility issues with the version from my package manager at the time of writing (early 2022).
2. Install python libraries: `sudo apt install python3-dev` on my Ubuntu system.
3. Already have a working printer set up through [CUPS](https://en.wikipedia.org/wiki/CUPS). You'll need to know the name of the printer (check [`lpstat -e`](https://www.cups.org/doc/man-lpstat.html) if you're not sure). If you don't have your printer set up you can use your desktop GUI or the `lpadmin` CLI to do so.

### Python dependencies, configuration and installation

1. Clone this repository. I'll assume this was cloned into `/home/ubuntu/matrix-printer-bot`.
2. Edit the create_subprocess_exec call in `file_handler.py`, replacing my printer name with the name of your actual printer.
3. Set up a virtual env and set it up with all the right dependencies: 
```
$ python3 -m venv ./env
$ source env/bin/activate
$ pip install -U pip
$ pip install -e .
```
4. Copy the top-level `matrix-printer-bot.service` file to an appropriate systemd directory: `sudo cp matrix-printer-bot.service /etc/systemd/system/`. Then edit that file if necessary to replace the `/home/ubuntu` paths with the path to the place you actually cloned the repository.
    
    You may also need to run `sudo systemctl daemon-reload` here.

5. Copy the config file (`sudo mkdir /etc/matrix-printer-bot && sudo cp sample.config.yaml /etc/matrix-printer-bot/config.yaml`) and then edit that file to pass in the actual matrix credentials and homeserver you'd like the bot to use.

6. Enable and start the service! `sudo systemctl start matrix-printer-bot && sudo systemctl enable matrix-printer-bot`.

### Trying it out.

By default the bot will only accept invitations from users whose accounts are on the same homeserver as the bot. If you're signed in to such an account, open a DM with the printer bot and send it a PDF (under the 10MB default size limit). You can also say `help` to be reminded of what the bot does.

## Project structure

The overall project structure is the same as that of a [standard nio-template bot](https://github.com/anoadragon453/nio-template#project-structure).

## Wishlist
* A config param for the name of the print queue, instead of having that hardcoded.
* Reporting an emoji reaction on success and the text of the error from CUPS to the room on failure, instead of writing only to the debug log.
* Using a networked CUPS API instead of `lp` to send jobs to the printer, so this bot can be run in Docker instead of requiring native libraries.
