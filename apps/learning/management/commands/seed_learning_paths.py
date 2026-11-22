from django.core.management.base import BaseCommand

from apps.learning.models import LearningPath, Lesson, LessonQuestion, LessonVisualFocus


# Classroom enrichment is path-level so every seeded lesson gains narration,
# takeaways, an educational animation and a short knowledge check without
# adding fabricated video files or external media.
PATH_CLASSROOM_CONTENT = {
    "phishing-detective": {
        "visual": LessonVisualFocus.PHISHING,
        "takeaways": [
            "Check the full sender address, not only the display name.",
            "Urgency and threats are common pressure tactics.",
            "Hover over links and compare the destination with the official site.",
            "Verify through a trusted app, website or phone number instead of replying.",
        ],
        "questions": [
            {
                "prompt": (
                    "A message says your account will close in 10 minutes and asks you "
                    "to confirm your password. What is the safest first step?"
                ),
                "choice_a": "Click the link and sign in quickly.",
                "choice_b": "Open the service through its official app or website and check there.",
                "choice_c": "Reply with your password so support can verify the account.",
                "choice_d": "Forward the message to friends to ask if it looks real.",
                "correct_choice": 2,
                "explanation": (
                    "Urgency is a pressure tactic. Reaching the service through a route "
                    "you already trust avoids the link in the suspicious message."
                ),
            },
            {
                "prompt": "Which detail is the strongest warning sign in a suspicious email?",
                "choice_a": "The sender address does not match the real organization.",
                "choice_b": "The email uses a friendly greeting.",
                "choice_c": "The message is longer than usual.",
                "choice_d": "The email contains a company logo.",
                "correct_choice": 1,
                "explanation": (
                    "Display names can be faked. The full sender address and link "
                    "destination reveal mismatches that are hard to spot at a glance."
                ),
            },
        ],
    },
    "password-guardian": {
        "visual": LessonVisualFocus.PASSWORD,
        "takeaways": [
            "Length and uniqueness matter more than predictable symbols.",
            "A passphrase of unrelated words can be strong and memorable.",
            "Never reuse a password across important accounts.",
            "MFA adds a second barrier when a password is stolen.",
        ],
        "questions": [
            {
                "prompt": "Why is a unique passphrase safer than reusing one short password?",
                "choice_a": "It is easier to type quickly.",
                "choice_b": "It reduces guessing and stops one breach from unlocking other accounts.",
                "choice_c": "It removes the need for multi-factor authentication.",
                "choice_d": "It makes password managers unnecessary.",
                "correct_choice": 2,
                "explanation": (
                    "Length increases the search space, and uniqueness limits the "
                    "damage when one service is compromised."
                ),
            },
            {
                "prompt": "What does multi-factor authentication add to sign-in security?",
                "choice_a": "A longer password requirement only.",
                "choice_b": "A hidden password that never changes.",
                "choice_c": "A second proof such as an app code, key or biometric check.",
                "choice_d": "Automatic sharing with trusted websites.",
                "correct_choice": 3,
                "explanation": (
                    "MFA combines something you know with something you have or are. "
                    "A stolen password alone is then not enough."
                ),
            },
        ],
    },
    "privacy-protector": {
        "visual": LessonVisualFocus.PRIVACY,
        "takeaways": [
            "Your footprint includes both shared posts and quietly collected traces.",
            "Personal details can support scams, impersonation and social engineering.",
            "Review privacy settings and connected apps regularly.",
            "Share less by default, especially location and identifying details.",
        ],
        "questions": [
            {
                "prompt": "What is a digital footprint?",
                "choice_a": "The information you leave online through posts, accounts and traces.",
                "choice_b": "A single saved password.",
                "choice_c": "A backup of your device.",
                "choice_d": "A type of network cable.",
                "correct_choice": 1,
                "explanation": (
                    "A footprint includes what you share on purpose and what services "
                    "collect passively, such as approximate location or activity."
                ),
            },
            {
                "prompt": "Which action best reduces unnecessary data exposure?",
                "choice_a": "Post your travel dates so friends can verify your plans.",
                "choice_b": "Keep location sharing on for every app.",
                "choice_c": "Use the same public profile everywhere.",
                "choice_d": "Make personal accounts private and remove unused connected apps.",
                "correct_choice": 4,
                "explanation": (
                    "Tighter audience settings and fewer connected apps reduce the "
                    "amount of personal information available to others."
                ),
            },
        ],
    },
    "network-navigator": {
        "visual": LessonVisualFocus.NETWORK,
        "takeaways": [
            "A router directs traffic between your local network and other networks.",
            "DNS turns names into addresses, while HTTPS encrypts web traffic.",
            "Use WPA2 or WPA3 and strong, unique Wi-Fi credentials.",
            "Confirm public network names before connecting and watch for warnings.",
        ],
        "questions": [
            {
                "prompt": "What does a router mainly do?",
                "choice_a": "Stores your passwords.",
                "choice_b": "Directs traffic between your local network and other networks.",
                "choice_c": "Replaces HTTPS encryption.",
                "choice_d": "Creates new websites.",
                "correct_choice": 2,
                "explanation": (
                    "A router connects networks and forwards packets to the right "
                    "destination, including the wider internet."
                ),
            },
            {
                "prompt": "Two café Wi-Fi names look almost identical. What should you do?",
                "choice_a": "Ask staff for the exact name and avoid sensitive tasks on untrusted networks.",
                "choice_b": "Join both networks to compare speed.",
                "choice_c": "Enter your account password to test the connection.",
                "choice_d": "Ignore the names and use any open network.",
                "correct_choice": 1,
                "explanation": (
                    "Lookalike networks can be created by attackers. Confirm the "
                    "exact name and keep HTTPS enabled."
                ),
            },
        ],
    },
    "mobile-defender": {
        "visual": LessonVisualFocus.MOBILE,
        "takeaways": [
            "A phone stores sensitive data, so screen locks and updates matter.",
            "Grant only permissions an app truly needs.",
            "Prefer official app stores and review developer details.",
            "Backups and device tracking help after loss or damage.",
        ],
        "questions": [
            {
                "prompt": "A flashlight app asks for access to your contacts. What should you do?",
                "choice_a": "Allow it because most apps ask for contacts.",
                "choice_b": "Allow it only at night.",
                "choice_c": "Question it and choose an app that needs fewer permissions.",
                "choice_d": "Share contacts with a friend first.",
                "correct_choice": 3,
                "explanation": (
                    "A permission should match the app's purpose. Unrelated access is "
                    "a reason to look for a safer alternative."
                ),
            },
            {
                "prompt": "Which combination best protects a lost smartphone?",
                "choice_a": "No lock, but frequent charging.",
                "choice_b": "Strong screen lock, updates, backups and device tracking.",
                "choice_c": "Only a patterned wallpaper.",
                "choice_d": "Turning off all notifications.",
                "correct_choice": 2,
                "explanation": (
                    "Layered protection reduces both the chance of access and the "
                    "impact if the device cannot be recovered."
                ),
            },
        ],
    },
    "data-defender": {
        "visual": LessonVisualFocus.DATA,
        "takeaways": [
            "Confidentiality, integrity and availability are the CIA model.",
            "Collect and keep only the data you truly need.",
            "Backups need to be protected and tested, not just created.",
            "Share sensitive files only with people who need them, through approved channels.",
        ],
        "questions": [
            {
                "prompt": "In the CIA model, what does availability mean?",
                "choice_a": "Anyone can see the data.",
                "choice_b": "Data is never changed.",
                "choice_c": "Data is stored without access controls.",
                "choice_d": "Authorized people can access the data when they need it.",
                "correct_choice": 4,
                "explanation": (
                    "Availability focuses on reliable access for authorized users, "
                    "while confidentiality and integrity cover secrecy and accuracy."
                ),
            },
            {
                "prompt": "What does the 3-2-1 backup guideline recommend?",
                "choice_a": "Three copies, on two storage types, with one copy off-site.",
                "choice_b": "Three passwords, two users and one device.",
                "choice_c": "One copy stored only on the main device.",
                "choice_d": "Three accounts and one unencrypted file.",
                "correct_choice": 1,
                "explanation": (
                    "Multiple copies on different media, including one kept separately, "
                    "protect against local loss and accidents."
                ),
            },
        ],
    },
}


INITIAL_PATHS = [
    {
        "title": "Phishing Detective",
        "slug": "phishing-detective",
        "description": (
            "Learn to recognize phishing emails, suspicious links, social engineering "
            "techniques, fake messages and online scams. Develop the skills to investigate "
            "suspicious messages and make safer decisions."
        ),
        "difficulty": LearningPath.Difficulty.BEGINNER,
        "estimated_duration": 45,
        "lessons": [
            {
                "title": "What Is Phishing?",
                "slug": "what-is-phishing",
                "description": "Understand phishing and why it is a common online threat.",
                "order": 1,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "What phishing is",
                        "Phishing is a trick where someone pretends to be a trusted person or organization to get you to reveal information, click a harmful link, or download a file.",
                        "",
                        "It is common because it is easy to send",
                        "Attackers can send many emails, texts, or direct messages at once. Even if only one person falls for the trick, it can be enough to steal a password or money.",
                        "",
                        "Common examples",
                        "• An email that looks like it came from your bank asking you to verify your account.",
                        "• A message saying a package could not be delivered and asking for payment details.",
                        "• A fake login page that looks like a real service.",
                        "• A text message offering a prize or warning about suspicious activity.",
                        "",
                        "The main idea",
                        "Slow down, check the source, and verify through a trusted route before you act.",
                    ]
                ),
            },
            {
                "title": "Spot the Warning Signs",
                "slug": "spot-the-warning-signs",
                "description": "Learn how to identify suspicious emails and messages.",
                "order": 2,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Sender inconsistencies",
                        "Check the full sender address, not just the display name. A message may say Support Team while the address uses an odd domain or extra characters.",
                        "",
                        "Urgency and pressure",
                        "Phishing messages often push you to act immediately. Phrases like act now or your account will close are designed to stop you from thinking carefully.",
                        "",
                        "Unexpected attachments and links",
                        "Be careful with attachments you were not expecting, especially documents that ask you to enable features or install something. Hover over links and compare the destination with the official site.",
                        "",
                        "Unusual requests",
                        "A real organization will not normally ask for your password, verification code, or payment card details by email or message.",
                        "",
                        "Quick checklist",
                        "• Does the sender address match the real organization?",
                        "• Is the message creating artificial urgency?",
                        "• Is the link destination trustworthy?",
                        "• Was the attachment expected?",
                        "• Is the request something you would normally receive this way?",
                    ]
                ),
            },
            {
                "title": "Verify Before You Click",
                "slug": "verify-before-you-click",
                "description": "Learn safer ways to inspect and verify suspicious messages.",
                "order": 3,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Use a trusted route",
                        "Instead of clicking a link in a message, open your browser and type the official website address yourself, or use the company's official app.",
                        "",
                        "Check independently",
                        "If a message claims to be from a person you know, contact them through a different method, such as a phone call or a known chat account.",
                        "",
                        "Inspect safely",
                        "Look at link destinations before clicking. On a computer, hovering over a link usually reveals the real address. Be cautious with shortened links because they hide the destination.",
                        "",
                        "Report suspicious messages",
                        "Most email and messaging services have a report or phishing button. Reporting helps protect you and other users.",
                        "",
                        "If you already clicked",
                        "Close the page, do not enter information, change any passwords you may have exposed, and tell someone who can help, such as your organization's support team.",
                    ]
                ),
            },
        ],
    },
    {
        "title": "Password Guardian",
        "slug": "password-guardian",
        "description": (
            "Learn password security, strong passphrases, password managers, "
            "multifactor authentication and ways to protect online accounts."
        ),
        "difficulty": LearningPath.Difficulty.BEGINNER,
        "estimated_duration": 45,
        "lessons": [
            {
                "title": "Password Security Basics",
                "slug": "password-security-basics",
                "description": "Understand how passwords protect accounts.",
                "order": 1,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "What a password does",
                        "A password proves that you are the person allowed to use an account. Weak or reused passwords make it easier for attackers to guess or reuse access.",
                        "",
                        "Common risks",
                        "• Short passwords that can be guessed quickly.",
                        "• Reusing the same password on many sites.",
                        "• Passwords based on names, birthdays, or common words.",
                        "• Falling for phishing pages that ask for your password.",
                        "",
                        "How attackers get passwords",
                        "Attackers may guess passwords, try passwords leaked from other websites, or trick people into typing them into fake login pages.",
                        "",
                        "The good news",
                        "You do not need to remember hundreds of complex strings. Use long unique passwords and let a password manager remember them for you.",
                    ]
                ),
            },
            {
                "title": "Create Strong Passphrases",
                "slug": "create-strong-passphrases",
                "description": "Learn how to create memorable and secure passwords.",
                "order": 2,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Length matters",
                        "Longer passwords are much harder to guess. A passphrase made of several random words can be both strong and easier to remember than a short messy password.",
                        "",
                        "Make each one unique",
                        "Every account should have its own password. If one website is compromised, a unique password stops attackers from using that same password elsewhere.",
                        "",
                        "Avoid predictable patterns",
                        "Do not use your name, username, birthday, favorite sports team, or simple substitutions like replacing o with 0.",
                        "",
                        "A useful pattern",
                        "Pick several unrelated words, add a number or symbol if the site allows it, and keep the whole phrase unique to that account.",
                        "",
                        "Example approach",
                        "Instead of a single word with a year, think of a phrase like purple-lantern-coffee-7 and use a different phrase for every account. A password manager can generate and store even stronger choices.",
                    ]
                ),
            },
            {
                "title": "Multifactor Authentication",
                "slug": "multifactor-authentication",
                "description": "Understand additional authentication security.",
                "order": 3,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "What MFA means",
                        "Multifactor authentication, often called MFA or two-factor authentication, requires more than just a password to sign in.",
                        "",
                        "Common factors",
                        "• Something you know, such as a password.",
                        "• Something you have, such as your phone or a security key.",
                        "• Something you are, such as a fingerprint or face scan.",
                        "",
                        "Why it helps",
                        "If an attacker steals your password, they still need the second factor. That extra step can stop many account takeovers.",
                        "",
                        "Safer options",
                        "Use an authenticator app or a security key when available. These are generally safer than codes sent by text message, which can be intercepted or simulated by attackers.",
                        "",
                        "Recovery matters",
                        "Save recovery codes in a safe place and keep your recovery contact details up to date.",
                    ]
                ),
            },
        ],
    },
    {
        "title": "Privacy Protector",
        "slug": "privacy-protector",
        "description": (
            "Understand digital privacy, personal information exposure, privacy "
            "settings, online tracking and how to protect your personal data."
        ),
        "difficulty": LearningPath.Difficulty.BEGINNER,
        "estimated_duration": 45,
        "lessons": [
            {
                "title": "Your Digital Footprint",
                "slug": "your-digital-footprint",
                "description": "Understand the information you leave online.",
                "order": 1,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "What a digital footprint is",
                        "Your digital footprint is the information you leave behind when you use websites, apps, and social networks. It includes posts, photos, comments, account details, and traces of what you search or buy.",
                        "",
                        "Active and passive footprints",
                        "Some information you share on purpose, such as a profile photo. Other information is collected quietly, such as approximate location or which pages you visit.",
                        "",
                        "Why it matters",
                        "Personal details can be used to build a profile about you. That profile may be used for advertising, scams, impersonation, or social engineering.",
                        "",
                        "Reduce what you share",
                        "Think before posting personal details such as your address, school, workplace, travel plans, or documents. Less shared information means less material for attackers to misuse.",
                    ]
                ),
            },
            {
                "title": "Privacy Settings",
                "slug": "privacy-settings",
                "description": "Learn how privacy settings help control personal information.",
                "order": 2,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Review your accounts",
                        "Most major apps and websites include privacy settings that control who can see your posts, profile details, location, and contacts.",
                        "",
                        "Start with the basics",
                        "• Make personal accounts private when possible.",
                        "• Limit who can find you by email or phone number.",
                        "• Turn off location sharing unless you need it.",
                        "• Review connected apps and remove ones you no longer trust.",
                        "",
                        "Permissions matter",
                        "An app may ask for access to your camera, microphone, contacts, or photos. Allow only what the app truly needs.",
                        "",
                        "Check regularly",
                        "Privacy settings change when apps update. Review them a few times a year and after major app changes.",
                    ]
                ),
            },
            {
                "title": "Protect Personal Information",
                "slug": "protect-personal-information",
                "description": "Learn how to reduce personal data exposure.",
                "order": 3,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Know what counts",
                        "Personal information includes your full name, address, phone number, email, date of birth, photos, documents, and account details.",
                        "",
                        "Think before oversharing",
                        "A harmless-looking post can reveal answers to security questions or give attackers details they can use to impersonate you.",
                        "",
                        "Share carefully",
                        "Send sensitive documents only through trusted channels. Remove unnecessary personal details before sharing screenshots or files.",
                        "",
                        "Use privacy tools",
                        "Strong passwords, MFA, privacy settings, and careful link checking all work together to reduce exposure.",
                        "",
                        "If information is exposed",
                        "Change affected passwords, enable MFA, and watch for suspicious messages that use the exposed details.",
                    ]
                ),
            },
        ],
    },
    {
        "title": "Network Navigator",
        "slug": "network-navigator",
        "description": (
            "Explore networking basics, Wi-Fi security, network threats, safe "
            "browsing and the fundamentals of protecting network connections."
        ),
        "difficulty": LearningPath.Difficulty.BEGINNER,
        "estimated_duration": 45,
        "lessons": [
            {
                "title": "Networking Fundamentals",
                "slug": "networking-fundamentals",
                "description": "Understand basic networking concepts.",
                "order": 1,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "What a network is",
                        "A network is a group of devices that can communicate with each other, such as computers, phones, printers, and servers.",
                        "",
                        "IP addresses",
                        "An IP address is like a delivery address for a device on a network. It helps data find the right destination.",
                        "",
                        "Routers",
                        "A router connects your local network to other networks, including the internet. It directs traffic between devices and the wider web.",
                        "",
                        "Common terms",
                        "• Wi-Fi: wireless access to a network.",
                        "• LAN: a local area network, usually in one home or office.",
                        "• DNS: the service that turns names like example.com into IP addresses.",
                        "• HTTPS: a secure version of web traffic that encrypts communication.",
                        "",
                        "Why it matters",
                        "Understanding these basics helps you notice when a connection or network behaves strangely.",
                    ]
                ),
            },
            {
                "title": "Wi-Fi Security",
                "slug": "wi-fi-security",
                "description": "Learn the fundamentals of secure Wi-Fi.",
                "order": 2,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Use strong encryption",
                        "Choose WPA2 or WPA3 security on your home Wi-Fi if your router supports it. Avoid older security modes such as WEP.",
                        "",
                        "Change default router settings",
                        "Routers often ship with default admin usernames and passwords. Change these before using the router, and keep the router software updated.",
                        "",
                        "Use a strong Wi-Fi password",
                        "A long unique Wi-Fi password helps stop unauthorized users from joining your network.",
                        "",
                        "Be careful with public Wi-Fi",
                        "Public networks may not protect your traffic from other users. Avoid sensitive tasks on networks you do not trust, or use a trusted VPN if one is available.",
                        "",
                        "Check before connecting",
                        "Confirm the network name with the place you are visiting. Attackers can create lookalike networks to trick people into connecting.",
                    ]
                ),
            },
            {
                "title": "Safe Network Habits",
                "slug": "safe-network-habits",
                "description": "Understand how to make safer networking decisions.",
                "order": 3,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Think before joining",
                        "Free Wi-Fi is convenient, but question any network that asks for personal information before connecting.",
                        "",
                        "Avoid risky interactions",
                        "Do not ignore browser security warnings about unsafe websites. Avoid downloading software from unfamiliar sources while on public networks.",
                        "",
                        "Keep devices updated",
                        "Operating system and router updates often fix security problems. Enable automatic updates where possible.",
                        "",
                        "Separate networks when you can",
                        "Many routers let you create a guest network for visitors or smart devices. This keeps less trusted devices away from your main computers.",
                        "",
                        "Observe changes",
                        "Unknown devices, slow connections, or unexpected network names can be signs to investigate.",
                    ]
                ),
            },
        ],
    },
    {
        "title": "Mobile Defender",
        "slug": "mobile-defender",
        "description": (
            "Learn smartphone security, app permissions, mobile threats, device "
            "protection and safe mobile habits."
        ),
        "difficulty": LearningPath.Difficulty.BEGINNER,
        "estimated_duration": 45,
        "lessons": [
            {
                "title": "Mobile Security Basics",
                "slug": "mobile-security-basics",
                "description": "Understand common smartphone security risks.",
                "order": 1,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Your phone is a computer",
                        "Smartphones store messages, photos, contacts, payment details, and account tokens. Protecting the device protects much of your digital life.",
                        "",
                        "Keep the operating system updated",
                        "Updates repair security weaknesses. Install them promptly and enable automatic updates when possible.",
                        "",
                        "Use a screen lock",
                        "Use a strong passcode, pattern, PIN, or biometric unlock. A short or predictable lock is easy to bypass.",
                        "",
                        "Beware common threats",
                        "• Malicious apps disguised as useful tools.",
                        "• Phishing links in messages and social apps.",
                        "• Fake charging stations or unsafe network connections.",
                        "• Stolen devices with weak locks.",
                        "",
                        "Small habits help",
                        "Lock your screen, do not leave your phone unattended, and review app installs carefully.",
                    ]
                ),
            },
            {
                "title": "Understanding App Permissions",
                "slug": "understanding-app-permissions",
                "description": "Learn how apps access device information.",
                "order": 2,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "What permissions do",
                        "Permissions let apps access device features or data, such as the camera, microphone, contacts, location, or photos.",
                        "",
                        "Allow only what is needed",
                        "A flashlight app does not need access to your contacts. If a permission seems unrelated to the app's purpose, question it.",
                        "",
                        "Review permissions regularly",
                        "Check your phone's settings and remove permissions for apps you no longer use or trust.",
                        "",
                        "Pay attention to location",
                        "Location access can reveal where you live or work. Choose while using the app instead of always when possible.",
                        "",
                        "Install from trusted stores",
                        "Official app stores are not perfect, but they provide more review and removal processes than unknown download sites.",
                    ]
                ),
            },
            {
                "title": "Secure Your Smartphone",
                "slug": "secure-your-smartphone",
                "description": "Learn practical ways to protect your mobile device.",
                "order": 3,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Use layered protection",
                        "Combine updates, a strong screen lock, careful app installation, and MFA on important accounts.",
                        "",
                        "Back up your device",
                        "Backups help you recover photos and data if your phone is lost, damaged, or reset.",
                        "",
                        "Install apps carefully",
                        "Read app names, developer details, and reviews. Watch for apps that copy the look of popular services.",
                        "",
                        "Turn on device tracking",
                        "Find My Device or similar tools can help locate, lock, or erase a lost phone.",
                        "",
                        "Review connected accounts",
                        "Remove old accounts and sign out of services you no longer use on the device.",
                    ]
                ),
            },
        ],
    },
    {
        "title": "Data Defender",
        "slug": "data-defender",
        "description": (
            "Learn data protection, backup strategies, secure file handling, "
            "confidentiality and responsible data management."
        ),
        "difficulty": LearningPath.Difficulty.BEGINNER,
        "estimated_duration": 45,
        "lessons": [
            {
                "title": "Understanding Data Security",
                "slug": "understanding-data-security",
                "description": "Learn the importance of protecting digital information.",
                "order": 1,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "What data security means",
                        "Data security is about keeping information safe from unauthorized access, accidental loss, and misuse.",
                        "",
                        "The CIA model",
                        "• Confidentiality: only the right people can see the data.",
                        "• Integrity: the data stays accurate and trustworthy.",
                        "• Availability: authorized people can access the data when needed.",
                        "",
                        "Types of sensitive data",
                        "Personal details, financial records, health information, customer lists, passwords, and backups can all be sensitive.",
                        "",
                        "Basic protection habits",
                        "Use strong access controls, encrypt sensitive information when appropriate, keep backups, and share only what is necessary.",
                        "",
                        "Why it matters for beginners",
                        "Good data habits at home and at work reduce the impact of mistakes, theft, and accidents.",
                    ]
                ),
            },
            {
                "title": "Backup Basics",
                "slug": "backup-basics",
                "description": "Understand why backups are important.",
                "order": 2,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Why backups matter",
                        "Files can be lost through accidents, hardware failure, ransomware, theft, or mistaken deletion. A backup gives you another copy to restore from.",
                        "",
                        "The 3-2-1 idea",
                        "A common guideline is to keep three copies of important data, on two different types of storage, with one copy stored off-site or in the cloud.",
                        "",
                        "How often to back up",
                        "Back up often enough that losing recent work would not be a serious problem. Important projects may need daily or automatic backups.",
                        "",
                        "Test your backups",
                        "A backup is only useful if it can be restored. Occasionally check that you can open and recover a file from it.",
                        "",
                        "Protect backups too",
                        "Backups can contain sensitive data. Encrypt them, protect access, and keep them separate from the main device.",
                    ]
                ),
            },
            {
                "title": "Handle Data Responsibly",
                "slug": "handle-data-responsibly",
                "description": "Learn responsible data handling.",
                "order": 3,
                "estimated_minutes": 15,
                "content": "\n".join(
                    [
                        "Collect less",
                        "Data minimization means collecting and keeping only the information you truly need. Less data means less risk.",
                        "",
                        "Store carefully",
                        "Use secure locations, strong access controls, and encryption where appropriate. Avoid keeping sensitive files in random folders or personal messaging apps.",
                        "",
                        "Share with care",
                        "Send sensitive data only to people who need it, through approved channels. Double-check recipients and attachments before sending.",
                        "",
                        "Dispose properly",
                        "Delete old copies when they are no longer needed. Use secure disposal for devices or drives that held sensitive information.",
                        "",
                        "Respect privacy",
                        "Responsible data handling also means following rules, respecting people's expectations, and being honest about how information is used.",
                    ]
                ),
            },
        ],
    },
]


def _narration_for(lesson_data):
    """Build a short local narration script from the existing lesson text."""
    paragraphs = [
        line.strip()
        for line in lesson_data["content"].splitlines()
        if line.strip() and not line.startswith("•")
    ]
    opening = " ".join(paragraphs[:3])
    return (
        f"Welcome to {lesson_data['title']}. {opening} "
        "Listen for the key idea, then try the knowledge check at the end."
    )


class Command(BaseCommand):
    help = "Seed six published CyberQuest learning paths and their introductory lessons."

    def handle(self, *args, **options):
        self.stdout.write("Seeding CyberQuest learning paths...")

        created_paths = 0
        created_lessons = 0
        created_questions = 0

        for path_data in INITIAL_PATHS:
            path_defaults = {
                key: value
                for key, value in path_data.items()
                if key not in {"slug", "lessons"}
            }
            path_defaults["is_published"] = True

            path, path_created = LearningPath.objects.get_or_create(
                slug=path_data["slug"],
                defaults=path_defaults,
            )
            if path_created:
                created_paths += 1

            enrichment = PATH_CLASSROOM_CONTENT.get(path_data["slug"], {})
            new_lessons = 0
            new_questions = 0

            for lesson_data in path_data["lessons"]:
                lesson_defaults = {
                    key: value for key, value in lesson_data.items() if key != "slug"
                }
                lesson_defaults["is_published"] = True
                lesson_defaults["narration_text"] = _narration_for(lesson_data)
                lesson_defaults["transcript"] = lesson_data["content"]
                lesson_defaults["key_takeaways"] = "\n".join(
                    enrichment.get("takeaways", [])
                )
                lesson_defaults["visual_focus"] = enrichment.get(
                    "visual", LessonVisualFocus.NONE
                )

                lesson, lesson_created = Lesson.objects.get_or_create(
                    learning_path=path,
                    slug=lesson_data["slug"],
                    defaults=lesson_defaults,
                )
                if lesson_created:
                    created_lessons += 1
                    new_lessons += 1
                else:
                    # Existing Day 5 lessons gain classroom content without
                    # changing their titles, order or text.
                    updates = {}
                    for field in ("narration_text", "transcript", "key_takeaways"):
                        if not getattr(lesson, field):
                            updates[field] = lesson_defaults[field]
                    if lesson.visual_focus == LessonVisualFocus.NONE:
                        updates["visual_focus"] = lesson_defaults["visual_focus"]
                    if updates:
                        Lesson.objects.filter(pk=lesson.pk).update(**updates)

                for order, question_data in enumerate(
                    enrichment.get("questions", []), start=1
                ):
                    _, question_created = LessonQuestion.objects.get_or_create(
                        lesson=lesson,
                        order=order,
                        defaults=question_data,
                    )
                    if question_created:
                        created_questions += 1
                        new_questions += 1

            path_status = "created" if path_created else "already present"
            self.stdout.write(
                f"- {path.title}: {path_status}, {new_lessons} new lesson(s), "
                f"{new_questions} new question(s)"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_paths} new path(s) and {created_lessons} new lesson(s). "
                f"Database now has {LearningPath.objects.count()} path(s), "
                f"{Lesson.objects.count()} lesson(s) and "
                f"{LessonQuestion.objects.count()} question(s). "
                f"Added {created_questions} new question(s)."
            )
        )
