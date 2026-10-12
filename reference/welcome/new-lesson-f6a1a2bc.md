<!-- CourseStack lesson '🛜 VPN Connectivity' (slug new-lesson-f6a1a2bc), captured 2026-10-12 from /api/student/events/<EV>/take -->

# 🛜 VPN Connectivity

> [!NOTE]
> **VPN connectivity is optional.** If you are playing entirely through the browser-based **AI Homebase**, you may skip this setup. You only need the VPN when you want your own computer or analysis VM to reach private CTF systems directly.

You may notice after starting a virtual machine, there is an **IP address** displayed on the deployable challenge cards!

This displayed **IP address** is the IP address of the virtual machine within the CTF environment.

If you would rather not use the _browser-based_ connection from clicking **<u>🖥️ Connect</u>** in the deployment card and you prefer a **direct connection**, you can connect to the CTF environment with _your own_ computer or virtual machine using the VPN!

**1. Click the <u>Systems</u> tab on the left side navigation bar:**

<img
  src="https://images.coursestack.com/a77e10fa-84d0-476b-a1b5-ab2cbab18c00/b52a5ea2-7091-45c5-bb28-8ab590609d7a"
  alt=""
  width=""
  height=""
/>
<p class="md-caption"><i>Left side navigation bar screenshot... <b>not a real interactive widget on this page!</b></i></p>

**2. At the very bottom, click the <u>Download VPN Config</u> button!**

<img
  src="https://images.coursestack.com/a77e10fa-84d0-476b-a1b5-ab2cbab18c00/ee210cd6-544f-41f3-abf1-ac3c6a0c8e9e"
  alt=""
  width=""
  height=""
/>
<p class="md-caption"><i>Left side navigation bar screenshot... <b>not a real interactive widget on this page!</b></i></p>

**3. Save the `huntress-ctf-2026-ai-arena.ovpn` file onto your computer or virtual machine.**

You will need an OpenVPN _client_ to be able to make use of this! Below are some light setup instructions that may help you on Linux or Windows:

## OpenVPN on Linux

On Linux, you can very likely install the **`openvpn`** command-line utility from your distribution's software repositories.

If you are using a Debian-based system like **Ubuntu** or **Kali Linux**, this will likely work best for you:

**1. Install `openvpn`:**

```bash
sudo apt install -y openvpn
```

If you have administrative privilege ("sudo permissions"), the `sudo` command will prompt you for your own local user account password, and will not display the characters on the screen as you type them out. Trust yourself to enter your own password correctly, press Enter, and let it install!

**2. Connect!**

```
sudo openvpn huntress-ctf-2026-ai-arena.ovpn
```

The command above assumes you have the **`huntress-ctf-2026-ai-arena.ovpn`** file in your current working directory. If you don't you can move the file there, or provide the full path to the downloaded file!

**3. Review:**

<img
  src="https://images.coursestack.com/a77e10fa-84d0-476b-a1b5-ab2cbab18c00/504dfa76-eade-4717-96ac-5ec84fcba80f"
  alt=""
  width=""
  height=""
/>
<p class="md-caption"><i>Successful <b><code>openvpn</code></b> connection on Kali Linux</i></p>

You should see output like the above! If you see `Initialization Sequence Completed`, then you are connected to the VPN! 😄

## OpenVPN on Windows

On Windows, typically the "easiest" way to get a VPN connection going is with the **OpenVPN Connect** GUI-based utility, that you can download and install from OpenVPN's website &mdash; link is here: [https://openvpn.net/client/](https://openvpn.net/client/)

<img
  src="https://images.coursestack.com/a77e10fa-84d0-476b-a1b5-ab2cbab18c00/5d2a8970-e2a2-46fb-9fae-460d77f2e15f"
  alt=""
  width=""
  height=""
/>
<p class="md-caption"><i><b>OpenVPN Connect for Windows download page screenshot... not an interactive widget on this page!</b></i></p>

**1. Download and install the OpenVPN Connect for Windows application.**

<img
  src="https://images.coursestack.com/a77e10fa-84d0-476b-a1b5-ab2cbab18c00/4f5c78ad-784a-40fa-b92e-1be32e0aec51"
  alt=""
  width=""
  height=""
/>

**2. On the bottom of the program interface, click <u>Upload File</u> to navigate and select the `huntress-ctf-2026-ai-arena.ovpn` file**

<img
  src="https://images.coursestack.com/a77e10fa-84d0-476b-a1b5-ab2cbab18c00/152ca129-8ea6-4982-8a3c-e6bb11c6ed74"
  alt=""
  width=""
  height=""
/>

**3. Click <u>Import</u>, <u>Connect</u>, and you should see "*Securely Connected!*"**

Now you should be able to ping and access the IP addresses referenced within the challenge deployment cards. This will give you a direct connection! Some protocols like HTTP, RDP, or others may be faster with this VPN connectivity, so we strongly recommend it.

