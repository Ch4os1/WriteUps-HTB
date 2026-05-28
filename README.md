# WriteUps-HTB (For CPTS) — 116 Boxes Pwned!

A complete collection of my **Hack The Box write-ups** used for **CPTS** and **OSCP preparation**.
Each write-up documents my process, methodology, and lessons learned while honing red team and pentesting skills.

> ⚙️ Difficulty ratings are subjective (x/10).
> 💡 Some write-ups include PoCs, but I highly recommend retrieving them from official sources.

---

## 🎮 Modes of Practice

HTB offers two primary modes:

- **Guided Mode** – Best for beginners. Follow structured hints and learning paths.
- **Adventure Mode** – Recommended once comfortable with Easy boxes. Mimics real exam conditions with minimal hints.

After Easy difficulty, I primarily switched to **Adventure Mode** for more authentic practice.

---

## 💻 View in Obsidian (Recommended)

To get the best reading and navigation experience, use [**Obsidian**](https://obsidian.md):

### Quick Setup

#### 1. Install Obsidian
- Download: https://obsidian.md
- Available for **Windows**, **macOS**, and **Linux**

#### 2. Clone & Open the Repository
```bash
# Clone the repo
git clone https://github.com/your-username/WriteUps-HTB.git
cd WriteUps-HTB

# Open in Obsidian:
# - Launch Obsidian
# - Click “Open folder as vault”
# - Select the cloned folder
```

---

## 🗂️ Folder Structure

<details>
<summary>Click to expand</summary>

	📁 ~/WriteUps-HTB
	├── 📁 Easy/
	│   ├── 📁 Linux/
	│   └── 📁 Windows/
	├── 📁 Medium/
	│   ├── 📁 Linux/
	│   └── 📁 Windows/
	├── 📁 Hard/
	│   ├── 📁 Linux/
	│   └── 📁 Windows/
	├── 📁 Insane/
	│   ├── 📁 Linux/
	│   └── 📁 Windows/
	├── 📁 AD/
	│   ├── 📁 Easy/
	│   ├── 📁 Medium/
	│   ├── 📁 Hard/
	│   └── 📁 Insane/
	└── 📁 Templates/
	    └── Writeup-Template.md

</details>

---

## 📊 CPTS Prep Progress (Static Snapshot)

| Category        | Completed | Progress        |
| --------------- | --------- | --------------- |
| 🟢 Easy         | 46 / 46   | ██████████ 100% |
| 🟡 Medium       | 30 / 30   | ██████████ 100% |
| 🔵 AD           | 30 / 30   | ██████████ 100% |
| 🔴 Hard (Linux) | 10 / 10   | ██████████ 100% |
| 🔗 Pro Lab      | 2 / 2     | ██████████ 100% |

---

## 🧩 Box Lists

### 🟢 Easy (46/46) 
<details>
<summary>Click to expand</summary>

**Classic Practice**
- Knife (2/10)
- Sunday (3/10)
- Keeper (1/10)
- Bashed (1/10)
- Beep (1/10)
- Armageddon (4/10)
- Blunder (3.5/10)
- Popcorn (1.5/10)
- Postman (4/10)
- Shocker (1/10)
- Access (3/10)
- Swagshop (3/10)
- Arctic (2/10)
- Blue (1/10)
- Buff (3/10)
- Devel (2/10)
- Jerry (1/10)
- Legacy (1/10)
- Netmon (1/10)
- Remote (2/10)
- Broker (1.5/10)
- Soccer (3.5/10)
- Sau (1/10)
- Dog (2.5/10)
- Help (4/10)
- Usage (3.5/10)
- LinkVortex (3/10)
- Pandora (4/10)
- Editorial (3.5/10)
- Networked (3/10)
- Support (5/10)
- Servmon (3/10)
- Mailing (3/10)
- Driver (3/10)
- Crafty (3/10)
- Granny (1/10)

**Adventure Mode (Exam Simulation)**
- CozyHosting (4/10)
- Busqueda (4/10)
- Broadlight (2/10)
- Delivery (3/10)
- MetaTwo (3/10)
- Trick (5/10)
- Shoppy (3/10)
- Sense (2/10)
- OpenAdmin (2/10)
- Heist (4.5/10)

</details>

---

### 🟡 Medium (30/30) 
<details>
<summary>Click to expand</summary>

- UpDown (5/10)
- Monitored (5/10)
- Book (6/10)
- Schooled (5/10)
- Redcross (7/10)
- Ready (6/10)
- Writer (8/10)
- Gobox (6/10)
- Bolt (8/10)
- Builder (3/10)
- Epsilon (5/10)
- Awkward (8.5/10)
- Iclean (4/10)
- Faculty (5/10
- BackendTwo (7.5/10)
- Aero (3.5/10)
- Trickster (8/10)
- Backfire (8.5/10)
- Chatterbox (3/10)
- SecNotes (4/10)
- Manager (4/10)
- Outdated (8.5/10)
- Agile (7.5/10)
- Jeeves (2.5/10)
- Hospital (8/10)
- Magic (3/10)
- Media (VulnLab - 4.5/10)
- POV (3.5/10)
- Craft (3.5/10)
- StreamIO (7/10)
</details>

---

### 🔵 AD (Total 30/30) - Mixed Difficulty 
<details>
<summary>AD labs (Click to expand)</summary>

**Easy**
- Active – (2/10)
- Sauna – (3/10)
- Timelapse – (3/10)
- Return – (1/10)
- Cicada – (2/10)
- Forest – (3/10)
- Fluffy – (3.5/10)

**Medium**
- Monteverde – (3.5/10)
- Cascade – (5/10)
- Administrator – (4.5/10)
- Certified – (5/10)
- Querier – (3/10)
- Scrambled – (7.5/10)
- Intelligence – (4/10)
- Escape – (2/10)
- TheFrizz – (5/10)
- Authority – (6.5/10)
- VulnCicada (VulnLab) – (7/10)
- TombWatcher – (4/10)
- Voleur – (5/10)
- Worker
- Fuse
- Sweep
- Shibbeloth
- Resolute
- Arkham
- Querier
- Lightweight
- Carrier
- Sniper

**Hard**
- Vintage – (7/10)
- Freelancer – (9/10)
- Redelegate (VulnLab) – (6/10)
- Analysis
- Mantis
- LustrousTwo
- Shibuya - (6/10)
- Flight - (6.5/10)
- Blackfield - (4/10)
- Search - (5.5/10)
- Object - (6/10)

**Insane**
- Rebound – (6.5/10)
- Ghost – (9.5/10)

</details>

---

### 🔴 Hard (Total 10/10) - (Web/SQL Focused) 
<details>
<summary>Click to expand</summary>

- Snoopy (8/10)
- Guardian (9/10)
- Kotarak (5/10)
- Holiday (5/10)
- Monitors (7/10)
- Jarmis - (6.5/10)
- Oouch - (9.5/10)
- Joker - (5/10)
- Falafel - (5/10)
- OneTwoSeven - (6/10)

</details>

---

### 🔗 Pro Labs (2/2) 
<details>
<summary>Click to expand</summary>

- **Dante**  <br>
- **Zephyr**
</details>

---

## 📚 References

- [OSCP-like Labs — NetSecFocus Trophy Room](https://docs.google.com/spreadsheets/u/1/d/1dwSMIAPIam0PuRBkCiDI88pU3yzrqqHkDtBngUHNCw8/htmlview#)
- [CPTS Prep Playlist by IppSec](https://www.youtube.com/playlist?list=PLidcsTyj9JXItWpbRtTg6aDEj10_F17x5)

---


> _“Repetition builds intuition. Precision builds mastery.”_
