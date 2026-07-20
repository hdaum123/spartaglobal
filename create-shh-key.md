Library
/
GitHub_SSH_Authentication.md


# GitHub SSH Authentication

## Aim

The aim of this task was to recreate my GitHub SSH authentication by
deleting the old SSH key, generating a new key pair, adding it to GitHub
and testing the connection.

> **Reminder:** Never store your `.ssh` folder or private keys inside a
> Git repository.

------------------------------------------------------------------------

# Step 1 - Delete the old SSH key

Open the `.ssh` folder and delete the old key pair.

``` bash
cd ~/.ssh
rm id_ed25519
rm id_ed25519.pub
```

Delete the old SSH key from **GitHub → Settings → SSH and GPG keys**.

Delete the test repository from GitHub.

------------------------------------------------------------------------

# Step 2 - Generate a new SSH key

``` bash
ssh-keygen -t ed25519 -a 100 -C "homaira-daum@tech610-work-laptop"
```

### Explanation

-   `ssh-keygen` -- creates an SSH key pair.
-   `-t ed25519` -- uses the Ed25519 encryption algorithm.
-   `-a 100` -- strengthens the private key using 100 KDF rounds.
-   `-C` -- adds a comment to identify the key.

When prompted:

``` text
Enter file in which to save the key (/c/Users/HomairaDaum/.ssh/id_ed25519):
```

I pressed **Enter**, so the default filenames were used:

``` text
id_ed25519
id_ed25519.pub
```

I then entered a memorable passphrase.

------------------------------------------------------------------------

# Step 3 - Start the SSH agent

``` bash
eval `ssh-agent -s`
```

### Explanation

This starts the SSH agent, which securely stores my private key while
I'm using Git.

------------------------------------------------------------------------

# Step 4 - Add the private key

``` bash
ssh-add ~/.ssh/id_ed25519
```

### Explanation

This loads my **private key** into the SSH agent.

> Do **not** add `id_ed25519.pub` because that is the public key.

------------------------------------------------------------------------

# Step 5 - Copy the public key

``` bash
cat ~/.ssh/id_ed25519.pub
```

Copy the entire output beginning with:

``` text
ssh-ed25519 AAAA...
```

Paste it into:

**GitHub → Settings → SSH and GPG keys → New SSH key**

Choose any title you like (for example **Tech610 Laptop**) and paste the
public key into the **Key** field.

------------------------------------------------------------------------

# Step 6 - Test the connection

``` bash
ssh -T git@github.com
```

The first time, GitHub may ask:

``` text
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Type:

``` text
yes
```

If everything is correct, you should see:

``` text
Hi hdaum123! You've successfully authenticated, but GitHub does not provide shell access.
```

------------------------------------------------------------------------

# SSH Authentication Diagram

``` text
                 GitHub
                    ▲
                    │
      Public Key (id_ed25519.pub)
                    ▲
                    │
         Copy using:
   cat ~/.ssh/id_ed25519.pub
                    │
──────────────────────────────────────

            Your Laptop

Generate key pair
ssh-keygen
      │
      ├── id_ed25519        (Private key)
      └── id_ed25519.pub    (Public key)

      │
      ▼
Start SSH agent
eval `ssh-agent -s`

      │
      ▼
Add private key
ssh-add ~/.ssh/id_ed25519

      │
      ▼
Test connection
ssh -T git@github.com
```

------------------------------------------------------------------------

# Key Learning Points

-   SSH creates a public and private key pair.
-   The private key stays on my laptop.
-   The public key is added to GitHub.
-   `ssh-add` loads the private key into the SSH agent.
-   `ssh -T git@github.com` tests that authentication works.
-   Never upload your private key or the `.ssh` folder to GitHub.
