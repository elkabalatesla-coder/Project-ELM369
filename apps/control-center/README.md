# Project ELM369 Control Center — v0.1.0

## Purpose
A standalone, browser-based prototype for an actual interactive on-screen keyboard and a mode-switching control dashboard.

## Run
Open `index.html` in a modern browser. No build step or external dependency is required.

## Included
- Clickable on-screen keyboard that enters text into the page's typing area.
- Physical keyboard typing into the same text area.
- Mode switching: Keyboard, Gamepad, Toggle Board, Custom Controller, Voice/AI, and Touch/Gesture.
- Mode-specific prototype controls and tool catalogs.
- Studio program and NFT Creator catalog panels.
- App-folder catalog organized by use case.
- Responsive layout for desktop and mobile screens.

## Safety and implementation boundaries
This is a front-end prototype. It does not register a system-wide input method, replace the device's Android/ChromeOS keyboard, control arbitrary applications, send commands to robots or other hardware, run shell commands, connect to a blockchain, or mint NFTs. Voice recognition and hardware gamepad integration are not connected. The folder panel is a catalog, not filesystem access.

Before production integration, add explicit adapters for each supported platform, permission and authorization gates, input-device capability detection, audit events, tests, and backend APIs. Keep blockchain signing and minting behind separate explicit user confirmation and transaction review.

## Project integrity
This prototype is added on the isolated branch `copilot/elm369-actual-keyboard-control-center-v0-1`. It does not modify `main` or merge/replace existing Project ELM369 files.
