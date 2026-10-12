<!-- CourseStack lesson '🏠 The AI Homebase' (slug -the-ai-homebase), captured 2026-10-12 from /api/student/events/<EV>/take -->

# 🏠 The AI Homebase

To help facilitate your use of AI, we provide for you a dedicated system as your **AI Homebase** with token credits included.

The **Homebase** VM is available to you at any time from the **Systems** listing on the left-hand navigation of the CTF platform.




> [!IMPORTANT]
> The **Reset** button on the AI Homebase System card performs a **factory reset.** If you press it, your Homebase will be reformatted to a fresh, clean slate and you will lose **all chats and files** stored on it.

## Enter the AI Homebase

1. Hover your mouse cursor over the **Power** drop-down on the bottom-left of the System card.
2. Click **Start** to turn on the VM.
3. Watch the VM status in the top-right of the card transition from a yellow **Starting** text to a green **Running** text.
4. Wait until the **Connect** button on the bottom-right is active.
5. Click **Connect** to be presented with your own AI Homebase environment!

> [!NOTE]
> The **AI Homebase** VM uses up your allotted _credits_ for compute time and AI tokens while it is on and running. **To maximize your play time, turn off the VM when you aren't using it!** You can pair once from Homebase and then reach the Game Master from your own setup without keeping the VM or VPN running. Private challenge targets may still need the VPN; see **The Game Master** and **Automating Your Solves**.

## Connect with SSH

SSH is available and encouraged if you prefer working in your own terminal. Connect to the CTF VPN as described in **VPN Connectivity**, then start your Homebase VM and use the IP address shown on its System card.

```bash
ssh HuntressCTF@<your-homebase-ip>
```

Your SSH username is **`HuntressCTF`**.

**This is the password for you to connect to the SSH account for the Homebase VM and the HuntressCTF user: `<homebase-password>`.**

Replace `<your-homebase-ip>` with your own VM's IP address. When SSH asks for the password, type it and press Enter; the characters will not appear as you type.

You can run administrative commands with `sudo`. If sudo asks for a password, use the same Homebase password above. For example, `sudo whoami` should print `root`.

## Use the AI workspace

The Homebase VM offers you readily available access to a coding agent and harness overtop of **[Claude Code](https://claude.com/product/claude-code)** and **[Codex](https://chatgpt.com/codex/)**.

You are welcome to still utilize any AI environment that you would like (**using your own tokens or AI subscriptions**), but in order to utilize token credits that we provide for you, you must use the **Homebase VM.**

This interface is prepared with an **`AGENTS.md`** file to instruct your AI agent to reach the Game Master service from within the CTF environment. You may download the **`AGENTS.md`** file for your own usage here:




The Homebase frontend is powered by **[T3 Code](https://t3.codes/)**, an open-source interface for AI coding agents. Credit to the T3 team!

## AI Models Available

Use the interface model picker to see the models enabled for your Homebase and choose the one you want to use.

> [!IMPORTANT]
> **To make the most of the allotted tokens we provide for you, we <u>_strongly recommend_</u> you use GPT-6 Luna within the Homebase VM.** Your allotted token credits replenish daily with new challenge releases at 9:00 AM Eastern Time.

## Things to Know

1. You can open a terminal within the **AI Homebase** VM and T3 Code interface! Makes command-line access easy once you click "Connect" on the system card.

![Top-right T3 Code toolbar showing the terminal drawer and right panel buttons.](https://images.coursestack.com/a8be0848-ea22-4644-8dda-99af6ac82b7e/4b6d0c2a-72b4-4e97-9b57-28adb76e5c3e)

In the top right of the interface, click the **Toggle Terminal Drawer (`Ctrl+J`)** button to instantly open a terminal on the bottom of the display...

![AI Homebase in T3 Code with the terminal drawer open below the chat.](https://images.coursestack.com/a8be0848-ea22-4644-8dda-99af6ac82b7e/c660928c-19a8-4c4e-a77f-c4cbfa5a2477)
... or click the **Toggle right panel (`Ctrl+Alt+B`)** to open a sidebar to open a new terminal, view fields, and more.

![T3 Code right panel showing the Terminal option in the Open a surface menu.](https://images.coursestack.com/a8be0848-ea22-4644-8dda-99af6ac82b7e/c69bbccd-29a0-4667-b257-8249fb0a45d9)

2. We have observed cases of the **AI Homebase** VM first starting up with a "Codex provider status" error.

![Codex provider status notification stating that provider status has not been checked in this session.](https://images.coursestack.com/a8be0848-ea22-4644-8dda-99af6ac82b7e/9551b874-9649-4594-a0f6-f4cc8690d88b)

**This should resolve on its own after a few seconds. Please wait for the system to finish initializing, it should not prohibit you from playing the game.**

3. You may see the **AI Homebase** display an **Update Available** notification. This notification is specifically referring to the underlying harness, **Codex** or **Claude Code**, that the T3 Code interface drives. This update notice may frequently appear because these tools release changes often. It is NOT an update notification pertaining to game playability; an update may fail if you choose to run it, but you _do not have to_ update and it should not prohibit you from playing the game.

![Codex update available notification with Settings and Update buttons.](https://images.coursestack.com/a8be0848-ea22-4644-8dda-99af6ac82b7e/091eb403-1a30-4886-99e5-76bf1ecd0f6c)

If you choose to update, it may fail with other scary looking red colored errors:

![Codex update failed status notification.](https://images.coursestack.com/a8be0848-ea22-4644-8dda-99af6ac82b7e/962742ed-98ab-4a7f-a458-773df6fd3ab2)

**Don't worry -- the game is still playable without needing to update.** You can use the Homebase VM as it is provided, but if you'd like more control and tuning, you can connect to the VPN and rig up your own AI your own way!

![Provider update failed notification stating that the update command exited with code 243.](https://images.coursestack.com/a8be0848-ea22-4644-8dda-99af6ac82b7e/93fb818f-fe76-4f94-accb-6b80502c03f2)

**Pardon our appearance during construction** -- we're still tryna get this whole concept and player experience just right, -- you _should_ be able to disregard those errors and still get to play!

4. We have observed cases of the **AI Homebase** starting up and immediately responding with "T3 Code could not load."

![T3 Code could not load screen with a Reload button.](https://images.coursestack.com/a8be0848-ea22-4644-8dda-99af6ac82b7e/7058ca66-30f0-41a4-81a2-ce9893dca415)

If you see this occur, and it does not proceed to the T3 interface after refreshing the page, please **Reset** your VM. **Again, please know that this process will remove your thread conversation history and files on the Homebase AI system.**

