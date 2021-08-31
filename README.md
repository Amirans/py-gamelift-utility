# Game Lift Utility

[GameLift](https://aws.amazon.com/gamelift/) Utility Written in Python for dealing with various Game Lift Tasks.

## Installation

Download [Python](https://www.python.org/downloads/).

Clone this Repository 

```bash
git clone https://github.com/Amirans/py-gamelift-utility.git
```
Install all the Requirements / Dependencies
```bash
pip install -r requirements.txt
```

## Usage

>GetGameLiftInstanceAccess [More Info](https://docs.aws.amazon.com/gamelift/latest/developerguide/fleets-remote-access.html)

```python
py GetGameLiftInstanceAccess.py

# Output Directory to Export/Output the Instance Access Details
Output Directory: 

# Set the Proffered AWS Region Or Leave Enter If the Displayed Region is Correct
Is Current AWS Region "AWS Region" Correct: (y/n)

# You Can either Enter a 'Fleet-Id' Or 'Build-Id' Accepted Formats are fleet-### or build-###
Enter a Fleet Id or Build Id:
```
Once the Instances are retrieved from the fleet , the script performs the following operations on the fleets/instances:

- Updates the port settings for the fleet and all of its instances to allow SSH or RDP connection.
the Script automatically detects whether the fleet's instances operating systems are Windows or Linux or both
Windows RDP : 22 / TCP
Linux SSH : 3389 / TCP
- It is Recommended to remove/revoke these updated port from the Fleets once remote access is no longer required.
- Creates a Info.txt and PrivateKey.pem for Linux Instances in the output directory.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
