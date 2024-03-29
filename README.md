# Setup
- Install python.
- Run _init-dependencies.bat or manually run the commands within the file to download necessary libraries.
- Adjust config in src files if you wish to use a different file path for the dump, otherwise it will be performed in the source repository.

# Image Scraper
Scrapes Jellyneo for mystery picture images and is easy to modify to scrape more categories.
- Use _run-imagescraper.bat or run ```python src/mysterypicsdl.py``` in the project directory.
- Only downloads shopkeeper / non-shopkeeper banner images by default. Includes config option to download more.

# Color Reader
The color reader takes a list of color hexcodes and returns images that contain those colors.
- Use _run-colorreader.bat.bat or run ```python src/mysterypicsdl.py``` in the project directory.
- Asks for list of color codes - you'll need an external color dropper tool for this
- Faster but less accurate - try using this first

# File Reader
The file reader takes an image file and returns images that contain the same colors as it.
- Use _run-colorreader.bat.bat or run ```python src/mysterypicsdl.py``` in the project directory.
- Asks for list of color codes - you'll need an external color dropper tool for this
- Uses threading to account for more work needing to be done
- Slower but more accurate - try adjusting color tolerance if the results aren't useful.