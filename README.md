# Climate Data

This is a guide on how to download data for CESM1 and CESM2.

We choose CESM2 and CESM1 from the
[models index](https://www.earthsystemgrid.org/project.html). For CESM2:
[dataset](https://www.earthsystemgrid.org/dataset/ucar.cgd.cesm2le.output.html)

Monthly data:

| Field      | link                                                                                       |
| ---------- | ------------------------------------------------------------------------------------------ |
| Ocean      | [link](https://www.earthsystemgrid.org/dataset/ucar.cgd.cesm2le.ocn.proc.monthly_ave.html) |
| Atmosphere | [link](https://www.earthsystemgrid.org/dataset/ucar.cgd.cesm2le.atm.proc.monthly_ave.html) |

## Requirements

-   Make sure `aria2` is installed in your system. It is used by the script to
    manage downloads.
-   Create your account on the gateway then on 'Account Home' retrieve your API
    Token and save it.
-   Go to the variable's page, for example CESM2 SSH
    [monthly average](https://www.earthsystemgrid.org/dataset/ucar.cgd.cesm2le.ocn.proc.monthly_ave.SSH.html),
    then click on the "History" tab and download the XML file in the "Source"
    field. Save the file as `SSH_monthly.xml`

The XML file should contain all the information we will need: file URL, size,
name, hash... We will retrieve the download links and send them to the
downloader script.

## Installation

```
pip install git+https://github.com/aghriss/clim_downloader
```

Installing the package will provide an executable that call
`clim_downloader.main:main`

## Usage

The package will extract the files from the XML file. Some files have multiple
versions, it will download the most recent one.

```bash
export TOKEN="put the token here"
clim_download --token $TOKEN \
--xml SSH_monthly.xml \
--target ./SSH \
--checksum true \ #use md5 checksum if available
--dry-run false \ #display information without downloading
--port 7800 \ #use different port for aria2 if another instance is running
```

To monitor the download speed and progress you can call (from within the same
python env):

```
aria2p -p 7800
```

The script will add `dataset.json` to --target that contains the files
informations.

./docs/demo.mp4
