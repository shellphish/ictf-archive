#include <iostream>
#include <string>
#include <vector>

using namespace std;

// Define a struct for phishing information
struct PhishingEmail {
    int id;
    string email;
    string message;
    string link;
    string mail_server;
    string suspicious;
    char sus_part;
};

// Function to add phishing information with custom parameters
void add_phishing_info(vector<PhishingEmail>& phishing_emails, int id, const string& email, const string& message, 
                       const string& link, const string& mail_server, const string& suspicious, char sus_part) {
    phishing_emails.push_back({id, email, message, link, mail_server, suspicious, sus_part});
}

void print_phishing_email(const vector<PhishingEmail>& phishing_emails, int index) {
    if (index >= 0 && index < phishing_emails.size()) {
        const PhishingEmail& email = phishing_emails[index];
        cout << "Question Number/ID: " << email.id << endl;
        cout << "Email: " << email.email << endl;
        cout << "Message: " << email.message << endl;
        cout << "Link: " << email.link << endl;
        cout << "Mail Server: " << email.mail_server << endl;
        cout << "---" << endl;
    } else {
        cout << "Invalid index" << endl;
    }
}

int main() {
    vector<PhishingEmail> phishing_emails;

    cout << "Greetings user! \nYour task is answering the questions provided by the code and you will need to use the provided sources to\n"
         << "recognize these social engineering attempts!" << endl;
         
    cout << "The ictf{} will be a combination of all the email IDS with suspicious activity! \nFormat Example being: ""ictf{123456789101112}"", so make sure you document your answers.\n" << endl;

    // Adding phishing emails
    add_phishing_info(phishing_emails, 1, "NorfolkStateHelpDesk@spartans.nsu.edu", "\nGreetings Jane Doe,\nWe hope this email finds you well. We are writing to inform you that your recent \nsupport request, with the reference number [10982329], is currently under review.", "N/A", "microsoft", "no", 'a');
    add_phishing_info(phishing_emails, 2, "Norfolk5tateHelpDesk@spartans.nsu.edu", "\nGreetings,\n You have a hold on your student account and it will prevent you from registering for classes.\nPlease sign into you account so you can take a look at the issue.\n Use the link www.Norfolk5tate.com/studentaccounts", "www.Norfolk5tate.com/studentaccounts", "microsoft", "yes", 'a');
    add_phishing_info(phishing_emails, 3, "Jenson.Grayson@protonmail.com", "\nHello!\nThis Jenson from work! I just wanted to know if you could take my shift for tomorrow thats all?", "N/A", "proton", "no", 'a');
    add_phishing_info(phishing_emails, 4, "googlecustomersupport@gmail.com", "\nHello there. \nIn a recent huge worldwide data leak google data leak your password showed up amoungst others. Please click this link to reset your password\nwww.googleresetpassword.com", "www.googleresetpassword.com", "gmail", "yes", 'e');
    add_phishing_info(phishing_emails, 5, "mike.jones@mitre.org", "\nHello, \nI'm from the help desk sector, some coworker has been going around gathering our passwords and we need to change passwords now.\n Please send me your new and old password before it too late!", "N/A", "mitre.org", "yes", 'c');
    add_phishing_info(phishing_emails, 6, "mrrobot@protonmail.com", "\nHi,\nIve obtained your banking information. To get your information back, send 500 dollars in bitcoin to my cashapp and all is well.", "N/A", "zoom", "yes", 'b');
    add_phishing_info(phishing_emails, 7, "security@paaypal.com", "\nDear Customer,\nWe noticed suspicious activity on your account. For your security, please confirm your information by clicking the link below.\nwww.paaypal.com/securitycheck", "www.paaypal.com/securitycheck", "paypal", "yes", 'a');
    add_phishing_info(phishing_emails, 8, "sarah.b@friendsmail.com", "\nHey!\nI saw this hilarious video and thought of you! You have to check it out when you get a chance. Here’s the link: www.friendsmail-videos.com\n\nTalk soon!", "www.friendsmail-videos.com", "friendsmail", "yes", 'd');
    add_phishing_info(phishing_emails, 9, "team@jobportal.com", "\nHello,\nThank you for using JobPortal! We wanted to remind you to update your profile to ensure you don’t miss out on potential job matches. You can log in at your convenience on our website.\n\nBest regards,\nThe JobPortal Team", "N/A", "jobportal", "no", 'a');
    add_phishing_info(phishing_emails, 10, "support@streamingfriends.com", "\nHi there!\nWe noticed you've been watching a lot of thrillers recently! Here’s a list of recommendations tailored just for you. Check them out here: www.streamingfriends-recs.com\n\nHappy Watching!", "www.streamingfriends-recs.com", "streamingfriends", "yes", 'd');
	add_phishing_info(phishing_emails, 11, "microsoft_support@microsoft.co", "\nDear User,\nWe noticed suspicious login attempts on your account. Click here to verify your account details.", "www.microsoft.co/verify", "microsoft", "yes", 'a');
    add_phishing_info(phishing_emails, 12, "donotreply@bank-secure.com", "\nDear Customer,\nThere is an unauthorized attempt to access your bank account. Confirm your details here.", "www.bank-secure.com/auth", "bank-secure", "yes", 'b');
    add_phishing_info(phishing_emails, 13, "notifications@amazon.com", "\nDear Customer,\nThank you for your recent purchase on Amazon! Your order #123456789 is on its way. You can track the delivery through your account.\nBest regards,\nThe Amazon Team", "www.amazon.com/your-orders", "amazon.com", "no", 'a');
    add_phishing_info(phishing_emails, 14, "alerts@bankofamerica.com", "\nDear Valued Customer,\nThis is a confirmation that a transaction of $50.00 was processed on your card ending in 1234. If you recognize this charge, no further action is needed.\nBest regards,\nBank of America Alerts", "N/A", "bankofamerica.com", "no", 'a');
    add_phishing_info(phishing_emails, 15, "billing@spotify.com", "\nHello,\nThis is a reminder that your Spotify Premium subscription will renew on the 15th of this month. No further action is required unless you wish to make changes to your subscription.\nBest,\nSpotify Billing Team", "N/A", "spotify.com", "no", 'a');
    add_phishing_info(phishing_emails, 16, "friend@outlook.com", "\nHey! Long time no talk! I thought of you when I found this amazing investment opportunity. Check it out!", "www.investment-news.com", "outlook", "yes", 'd');
    add_phishing_info(phishing_emails, 17, "prizes@luckywinner.com", "\nCongratulations! You have won a $500 Amazon gift card! Claim your prize here.", "www.luckywinner.com/claim", "luckywinner", "yes", 'c');
    add_phishing_info(phishing_emails, 18, "support@netflix.com", "\nHi there,\nWe noticed you finished the latest season of your favorite show! Here are some similar recommendations that might interest you. Log in to explore.\nHappy watching!\nThe Netflix Team", "www.netflix.com/recommendations", "netflix.com", "no", 'a');
    add_phishing_info(phishing_emails, 19, "admin@campushelpdesk.edu", "\nDear Student,\nYour campus account is set to expire. Confirm your email here to continue using services.", "www.campushelpdesk.edu/renew", "campushelpdesk", "yes", 'a');
    add_phishing_info(phishing_emails, 20, "team@jobportal.com", "\nHello,\nThank you for using JobPortal! We wanted to remind you to update your profile to ensure you don’t miss out on potential job matches. You can log in at your convenience on our website.\nBest regards,\nThe JobPortal Team", "www.jobportal.com", "jobportal.com", "no", 'a');





	for (int i = 0; i < phishing_emails.size(); ++i) {
        string user_answer, other_user_answer;
        
        while (true) {
            print_phishing_email(phishing_emails, i);
            cout << "Does this email have anything suspicious? \nType 'yes' or 'no'" << endl;
            cin >> user_answer;

            if (user_answer == phishing_emails[i].suspicious) {
                cout << "Correct!\n" << endl;

                if (user_answer == "yes") {
                    cout << "What social engineering principle is used (just type the letter)?\nA) Typosquatting\nB) Intimidation\nC) Urgency\nD) Familiarity\nE) Hoax" << endl;
                    cin >> other_user_answer;

                    if (other_user_answer[0] == phishing_emails[i].sus_part) {
                        cout << "Correct!\n" << endl;
                        break;  // Exit the loop to move to the next email
                    } else {
                        cout << "Nope, try again.\n" << endl;
                        return 0;
                    }
                }

                break;  // Exit the loop to move to the next email
            } else {
                cout << "Nope, try again.\n" << endl;
                return 0;
            }
        }
    }

    // Answer Key
    cout << "Answer Key" << endl;
    cout << "Q2: A \nThis is typosquatting because the social engineer put a 5 instead of an S to trick the recipient due to the characters looking similar.\n";
    cout << "Q4: E \nThis is a hoax because Google hasn't had a data leak in recent history.\n";
    cout << "Q5: C \nThis is using urgency because the social engineer is trying to get the recipient to act fast!\n";
    cout << "Q6: B \nThis is intimidation because they are scaring the recipient into believing that their banking information has been compromised.\n";
    cout << "Q7: A \nThis is typosquatting because the social engineer's email name spells 'Paypal' incorrectly, which is an easy mistake to miss.\n";
    cout << "Q8: D \nThis is familiarity because Sarah B is pretending that they know the recipient.\n";
    cout << "Q10: D \nThis is familiarity because the fake movie platform is presenting that the recipient has an account with them.\n";
    cout << "Q11: A \nThis is typosquatting because the social engineer's email uses 'microsoft.co' instead of the real 'microsoft.com'.\n";
    cout << "Q12: B \nThis is intimidation because the email is designed to scare the recipient into acting quickly.\n";
    cout << "Q16: D \nThis is familiarity because the sender is pretending to know the recipient personally.\n";
    cout << "Q17: C \nThis is urgency because the social engineer is enticing the recipient to claim the prize fast.\n";
    cout << "Q19: E \nThis is a hoax as it falsely claims suspicious activity.\n";
	

    cout << "Thank you! ;-)" << endl;
	//flag ictf{245678101112161719}
    return 0;
}
