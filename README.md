# PyCon Singapore 2026 🐍

## Orchestrating Distributed Cloud Infrastructure with Pulumi and PyInfra

> A Python-First Paradigm for Provisioning and Configuration

📅 **Date:** 20 June 2026  
📍 **Venue:** Lifelong Learning Institute, Singapore  
🎤 **Speaker:** Piti Champeethong — MongoDB Senior Consulting Engineer | Microsoft MVP

---

### 📖 Abstract

Modern cloud architectures demand a massive array of specialized tools — HCL, YAML, Bash, and custom DSLs — creating operational overhead and cognitive fragmentation. This session demonstrates how Python can unify the entire infrastructure lifecycle using **Pulumi** (declarative cloud provisioning) and **PyInfra** (agentless server configuration) to deploy a 3-node MongoDB Replica Set on Azure.

### 🎯 What You'll Learn

- Why "Infrastructure as Python" (IaPy) eliminates tool sprawl and context-switching
- How Pulumi provisions cloud resources with full Python logic, type safety, and testing
- How PyInfra configures servers via SSH without agents or YAML
- The **Metadata Handoff Pattern** — connecting Pulumi outputs directly to PyInfra inputs
- Production patterns: dry-runs, testing, secrets management, and CI/CD integration

---

### 🗂 Repository Structure

```
pyconsg26/
├── index.html          # Slide deck (open in browser)
├── styles.css          # Presentation styles
├── slides.js           # Navigation & syntax highlighting
├── demo/
│   ├── README.md       # Step-by-step demo guide
│   ├── pulumi/         # Azure VM provisioning code
│   └── pyinfra/        # MongoDB configuration code
└── references/
    └── PyConSG-2026.pdf
```

### 🚀 View the Slides

Live site: [pyconsg26.mrpiti.dev](https://pyconsg26.mrpiti.dev)

Open `index.html` in your browser, or use the keyboard shortcuts:
- **← / →** — Navigate slides
- **Space** — Next slide
- **Home / End** — Jump to first/last slide

### 🎮 Advanced Controls

**Sidebar Navigation:**
- **Click** the hamburger toggle button (bottom-left corner) to hide/show the sidebar
- **Press 'S'** to toggle sidebar visibility with a keyboard shortcut
- **Sidebar state persists** across page reloads via browser localStorage

**Additional Shortcuts:**
- **Escape** — Close the expanded architecture diagram (when clicked)

**Code Blocks:**
The presentation includes syntax-highlighted code for Python, YAML, Bash, and Jinja2 templates with automatic language detection.

### 🔧 Run the Demo

See the [demo/README.md](demo/README.md) for full step-by-step instructions to deploy a 3-node MongoDB Replica Set on Azure.

---

### 🔗 Connect

- **LinkedIn:** [linkedin.com/in/pitichampeethong](https://www.linkedin.com/in/pitichampeethong/)
- **GitHub:** [github.com/ninefyi](https://github.com/ninefyi)
- **MVP Profile:** [Piti Champeethong](https://mvp.microsoft.com/en-US/MVP/profile/a711758c-c801-45cb-8cea-e405ad824ac8)
