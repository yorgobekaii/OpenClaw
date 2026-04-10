### Installation Requirements

To successfully install and run OpenClaw on a fresh device, follow the steps and ensure your system meets the requirements listed below.

#### 1\. **Supported Operating Systems**

*   **Fully Supported:**
    
    *   **Linux** (Recommended: Ubuntu/Debian)
        
    *   **macOS**
        
    *   **Windows** (WSL2 recommended for full compatibility)
        
*   **Best Practical Setup:**
    
    *   **Best All-Around:** Ubuntu 24.04 LTS
        
    *   **Best Windows Option:** Windows 11 with WSL2 (Ubuntu)
        
    *   **Best Remote Host:** Linux VM/VPS
        

#### 2\. **Required Software and Versions**

*   **Node.js:**
    
    *   **Recommended Version:** Node 24
        
    *   **Minimum Version Supported:** Node 22.14+
        
*   **npm**:
    
    *   Required for package management if using npm to install.
        
*   **OpenClaw CLI:**
    
    *   npm install -g openclaw@latest
        
*   **Package Manager:**
    
    *   **pnpm** is used internally but is **optional** unless you are working with the source code.
        
*   **Core Runtime Dependencies:**OpenClaw depends on several Node.js libraries, including:
    
    *   sharp, express, dotenv, playwright-core, sqlite-vec, hono, zod, etc.
        
*   **Optional Native Dependencies (for specific setups):**
    
    *   sharp, @napi-rs/canvas, node-pty, node-llama-cpp, etc.
        

#### 3\. **Installation Methods**

*   **For Normal Users (recommended path):**
    
    *   npm install -g openclaw@latest
        
        *   Use the official shell installer, or install via npm:
            
    *   **Windows (WSL2 recommended):**
        
        *   Use the PowerShell installer or follow the Linux installation steps inside WSL.
            
*   openclaw onboard --install-daemon
    
*   **Installing from Source:**
    
    *   pnpm installpnpm ui:buildpnpm build
        

#### 4\. **Configuration Files and Environment Variables**

*   **Main Configuration File:**
    
    *   Located at ~/.openclaw/openclaw.json
        
    *   **Format:** JSON5
        
    *   If the file is missing, OpenClaw will run with default settings.
        
*   **Environment Variables:**
    
    *   **Core Path Overrides:**
        
        *   OPENCLAW\_HOME, OPENCLAW\_STATE\_DIR, OPENCLAW\_CONFIG\_PATH
            
    *   **Authentication/Startup:**
        
        *   OPENCLAW\_GATEWAY\_TOKEN, OPENCLAW\_GATEWAY\_PASSWORD
            
    *   **Logging:**
        
        *   OPENCLAW\_LOG\_LEVEL
            
    *   **Other important variables include:**
        
        *   OPENCLAW\_APNS\_RELAY\_BASE\_URL, OPENCLAW\_DISABLE\_BUNDLED\_PLUGIN\_POSTINSTALL
            

#### 5\. **Network Setup Requirements**

*   **Local-Only Setup:**
    
    *   No special networking required if running only locally (default access at http://127.0.0.1:18789/).
        
*   **Remote/Private Access (Optional):**
    
    *   **Tailscale** is recommended for secure access but optional.
        
    *   **Tailscale Modes:**
        
        *   serve (Tailnet-only HTTPS proxying)
            
        *   funnel (public HTTPS via Tailscale Funnel)
            
        *   Direct tailnet bind (for direct listen on the tailnet IP)
            
*   **Ports to Ensure Access:**
    
    *   Primary Gateway port: **18789**
        

#### 6\. **Required External Service Credentials**

To use OpenClaw with AI models and channels, you'll need:

*   **Model Provider API Key:** OpenAI, Anthropic, OpenRouter, Google, etc.
    
*   **Channel-Specific Credentials:** For services like Telegram, Discord, WhatsApp, etc.
    

Without these, OpenClaw can install but will not provide functional AI responses.

#### 7\. **Specific Setup Steps on a Fresh Device**

*   **For Windows (via WSL2 recommended):**
    
    1.  Install **WSL2** and **Ubuntu**.
        
    2.  Enable systemd in WSL.
        
    3.  Install **Node 24** inside WSL.
        
    4.  Install **OpenClaw**.
        
    5.  openclaw onboard --install-daemon
        

#### 8\. **Testing the Installation**

After setting up, run these tests to ensure everything is functioning properly:

1.  **Basic Smoke Test:**
    
    *   Check install: openclaw --help
        
    *   Verify gateway status: openclaw gateway status
        
    *   Open the dashboard: openclaw dashboard
        
    *   Access via http://127.0.0.1:18789/
        
    *   Send a test message and confirm model response.
        
2.  **Config Validation:**
    
    *   Run: openclaw doctor
        
    *   If needed: openclaw doctor --fix
        

#### 9\. **Optional Tools for Enhanced Usability or Performance**

*   **Tailscale** for secure remote access
    
*   **Docker** for containerized deployments
    
*   **Git** for workspace and source management
    
*   **pnpm** if building from source
    

#### 10\. **Known Compatibility Issues/Caveats**

*   **Node Version Mismatch:** Use **Node 24** to avoid discrepancies in the docs.
    
*   **TLS Issues with nvm:** Ensure NODE\_EXTRA\_CA\_CERTS is correctly set if using nvm.
    
*   **Native Modules Issues:** sharp, node-pty, canvas can cause installation issues on specific systems (e.g., minimal Linux distros, Windows).