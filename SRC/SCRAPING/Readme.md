---

# 🌌 SRC/SCRAPING: The Enchanted Workshop of Title Tailors 🌟

## Overview 🌐
In the mystical chamber of SRC/SCRAPING within the grand realm of Title Tailors, we weave together the art of Python scripting and the craft of Docker to transform data into a tapestry of insights. Guided by the arcane wisdom of `.env` and `.json` scrolls, our journey extends into the ethereal cloud realms of Google Cloud Storage.

## Magical Features 🔮
- **Data Conjuring** 📜: With scripts as our wands, we summon data from the digital ether with precision and intent.
- **Data Alchemy** 🧪: Like alchemists, we transmute raw data into golden insights, rich with meaning.
- **Cloudward Ascension** ☁️: Securely sending our alchemized data to the celestial vaults of Google Cloud Storage.

## Spellbook (Getting Started) 📖
### Mystic Tools (Prerequisites) 🛠️
- Docker, the mystical vessel for our computational odyssey.
- A Google Cloud Platform account, a portal to the cloud kingdoms.
- The `.env` and `.json` scrolls for casting configuration spells (details below).

### Enchantment Ritual (Installation) 🧙‍♂️
1. Summon the essence of Title Tailors:
   ```
   git clone https://github.com/karthik0899/Title-Tailors.git
   ```
2. Glide into the SRC/SCRAPING sanctum:
   ```
   cd Title-Tailors/SRC/SCRAPING
   ```
3. Call forth the Docker image:
   ```
   docker pull title-tailors
   ```

### Configuration 🛠️
- Employ the Streamlit crystal to craft a `.env` scroll, imbuing it with essential environmental variables.
- Secure a `.json` scroll with the necessary configurations, especially for Google Cloud Storage rituals.

### Usage 🚀
Invoke the Docker container with the power of your configuration scrolls:
```
docker run --env-file .env -v $(pwd)/your-config.json:/app/config.json title-tailors
```
This incantation activates the `Extraction_file.py` script, channeling the energies of the `.env` and `.json` scrolls.

## Key Scripts 📜
- **Extraction_file.py**: The chief script, orchestrating the symphony of data extraction and ascension.
- **py_functions_data.py**: A tome of refined functions for data manipulation and celestial uploads.

## Streamlit Oracle 🔮
- Consult our Streamlit oracle to effortlessly generate your `.env` scroll and receive a bespoke Docker run command for your unique setup.

## Potion Ingredients (Dependencies) 🧪
The alchemical components are listed in the [Book of Requirements](https://github.com/karthik0899/Title-Tailors/blob/main/SRC/SCRAPING/requirements.txt).

## Sacred License 📜
This enchanted workshop and its secrets are bound by the MIT Enchantment. Peruse the [LICENSE](https://github.com/karthik0899/Title-Tailors/blob/main/LICENSE) scroll for the sacred text.

---

