use std::io;
use std::fs;
use std::process;
use std::path::PathBuf;
use std::path::Path;

use rand::{thread_rng, Rng};
use rand::distributions::Alphanumeric;
use rand::prelude::*;
use rand_seeder::{Seeder};
use rand_pcg::Pcg64;

use md5;
use serde::{Serialize, Deserialize};

const RW_DIR: &str = "/home/chall/service/rw/";

fn read_line() -> String {
    let mut buffer: String = String::new();
    buffer.clear();
    io::stdin()
        .read_line(&mut buffer)
        .expect("Fail to read line from user!");
    if buffer.ends_with('\n') {
        buffer.pop();
    }
    if buffer.len() > 0x100 {
        println!("Too long!");
        process::exit(-1);
    }
    buffer
}

fn gen_rand_string(num: usize) -> String {
    thread_rng()
        .sample_iter(&Alphanumeric)
        .take(num)
        .map(char::from)
        .collect()
}

#[derive(Serialize, Deserialize, Clone)]
enum Event {
    Balance(BalanceEvent),
    Stock(StockEvent),
}

#[derive(Serialize, Deserialize, Clone)]
struct BalanceEvent {
    action: String,
    amount: u32,
    age: u8,
}

#[derive(Serialize, Deserialize, Clone)]
struct StockEvent {
    action: String,
    stock_id: usize,
    share: u32,
    price: u32,
    age: u8,
}

#[derive(Serialize, Deserialize)]
pub struct Game {
    age: u8,
    hash: String,
    save_file: String,
    promise: bool,
    events: Vec<Event>,
    stock_prices: [u32; 4],
    diary: String,
    trans: bool,

    hype: u8,
    accident: u8,
    anya: u8,
    dark: u8,
    double: bool,
}

impl Game {
    pub fn new() -> Game {
        return Game {
            save_file: String::new(),
            hash: String::new(),
            age: 0,
            promise: false,
            events: Vec::new(),
            stock_prices: [204, 39, 10, 137],
            diary: String::new(),
            trans: true,
            hype: 0,
            accident: 0,
            anya: 0,
            dark: 0,
            double: false
        };
    }

    fn get_balance(&self) -> u32 {
        let mut balance: u32 = 0;
        for event in &self.events {
            match event {
                Event::Balance(event)  => {
                    match event.action.as_ref() {
                        "add" => {balance += event.amount;}
                        "sub" => {balance -= event.amount;}
                        _ => {
                            println!("Something is wrong!");
                            process::exit(-1);
                        }
                    }
                }
                Event::Stock(event) => {
                    match event.action.as_ref() {
                        "buy" => {balance -= event.price*event.share;}
                        "sell" => {balance += event.price*event.share;}
                        "send" | "recv" => {}
                        _ => {
                            println!("Something is wrong!");
                            process::exit(-1);
                        }
                    }
                }
            }
        }
        balance
    }

    fn get_share(&self, stock_id: usize) -> u32 {
        let mut share: u32 = 0;
        for event in &self.events {
            match event {
                Event::Stock(event) => {
                    if event.stock_id != stock_id {
                        continue;
                    }
                    match event.action.as_ref() {
                        "buy" | "recv" => {share += event.share;}
                        "sell" | "send" => {share -= event.share;}
                        _ => {
                            println!("Something is wrong!");
                            process::exit(-1);
                        }
                    }
                }
                _ => {}
            }
        }
        share
    }

    fn read_i8(&self) -> i8 {
        let buffer: String = read_line();
        buffer.parse().unwrap_or(0)
    }

    fn read_u8(&self) -> u8 {
        let buffer: String = read_line();
        buffer.parse().unwrap_or(0)
    }

    fn read_u32(&self) -> u32 {
        let buffer: String = read_line();
        buffer.parse().unwrap_or(0)
    }

    fn get_save_path(&self, save_file: &str) -> PathBuf {
        let mut path = PathBuf::new();
        let dir = fs::canonicalize(RW_DIR)
                            .expect("there is something wrong with the RW directory");
        path.push(dir);
        path.push(save_file);
        path
    }

    fn save_state(&self) {
        let path = self.get_save_path(&self.save_file);
        let serialized = serde_json::to_string(&self).unwrap();
        fs::write(path, serialized)
            .expect("Unable to write serialized data to game save!");
    }

    fn load_state(&self, save_file: &str) -> Game {
        let path = self.get_save_path(save_file);
        let serialized = fs::read_to_string(path)
            .expect("Unable to read game save file");
        serde_json::from_str(&serialized).unwrap()
    }

    fn action_menu(&self) -> i8 {
        println!("At the age of {}, what do you want to do?", self.age);
        println!("1. Pass Time.");
        println!("2. Write Diary.");
        println!("3. Read Diary.");
        println!("4. Go to Carnival.");
        if self.age >= 8 {
            println!("5. Part time job at uncle Sam's grocery store.");
        }
        if self.age >= 18 {
            println!("6. Trade some meme stocks, how exciting!");
        }
        println!("126. Show Assets.");
        println!("127. Save the game and quit.");
        let choice = self.read_i8();
        match choice {
            1|2|3|4|126|127 => {}
            5 => {
                if self.age < 8 {
                    return -1;
                }
            }
            6 => {
                if self.age < 18 {
                    return -1;
                }
            }
            7 => {}
            _ => {
                println!("I don't understand you!");
                return -1;
            }
        }
        choice
    }

    fn pass_time(&self) {
        println!("You lie down on your bed, doing nothing.");
        return;
    }

    fn part_time(&mut self) {
        println!("Uncle Sam gives you $256 as the reward for your work.");
        let event = BalanceEvent {action: "add".to_string(),
                                             amount: 0x100,
                                             age: self.age};
        self.events.push(Event::Balance(event));
    }

    fn carnival(&mut self) {
        println!("You play whack-a-mole and win a platypus toy. What a day!");
        if self.age == 5 {
            println!("You go out of the carnival area and stumble across a perfect spot for stargazing.");
            println!("You meet a girl. You two make a rabbit constellation using the moon as its belly.");
            println!("You give her the platypus toy and agree to regroup on the moon if one of you get lost or get separated.");
            self.promise = true;
        }
        return;
    }

    fn stock(&mut self) {
        println!("Which stock do you want to trade?");
        println!("1. GameStop");
        println!("2. AMC");
        println!("3. BlackBerry");
        println!("4. ForRiver");
        let stock_id: u8 = self.read_u8();
        if stock_id > 4 {
            println!("The stock does not exist!");
            return;
        }
        let stock_id: usize = stock_id as usize;

        println!("What do you want to do with it?");
        println!("1. Buy");
        println!("2. Sell");
        let action: u8 = self.read_u8();

        println!("How many shares?");
        let share: u32 = self.read_u32();

        let price: u32 = self.stock_prices[stock_id-1];
        match action {
            1 => {
                let balance = self.get_balance();
                if price * (share as u32) > balance {
                    println!("You can't afford it!");
                    return;
                }
                let event = StockEvent {action: "buy".to_string(),
                                                  stock_id: stock_id,
                                                  price: price,
                                                  share: share,
                                                  age: self.age};
                self.events.push(Event::Stock(event));
            }
            2 => {
                let hold_share = self.get_share(stock_id);
                if share > hold_share {
                    println!("You don't have enough shares to sell!");
                    return;
                }
                let event = StockEvent {action: "sell".to_string(),
                                                  stock_id: stock_id,
                                                  price: price,
                                                  share: share,
                                                  age: self.age};
                self.events.push(Event::Stock(event));
            }
            _ => {
                println!("You can't do that!");
                return;
            }
        }
    }

    fn write_diary(&mut self) {
        println!("What do you feel like to write today?");
        let diary: String = read_line();
        self.diary = diary;
    }

    fn read_diary(&self) {
        if self.diary.len() == 0 {
            println!("You didn't write anything :(");
        } else {
            println!("You wrote something in the past:");
            println!("{}", self.diary);
        }
    }

    fn transaction(&mut self) {
        let mut good = false;
        let mut msg: &str = "";
        let hold = self.get_share(1);
        if self.age < self.hype {
            msg = "Who are you?";
        } else if !self.trans {
            msg = "You are being too greedy. No shares for you!";
        } else if hold == 0 {
            msg = "You don't like GameStop? There is not much to talk with you.";
        } else {
            good = true;
        }
        println!("Yo, I'm DeepFuckingValue.");
        if !good {
            println!("{}", msg);
            return;
        }

        println!("Welcome to the dark web!");
        println!("I am giving back to my community due to Covid-19!");
        println!("All GameStock shares sent to my address below will be sent back doubled.");
        println!("If you send 1000 shares, I will send back 2000 shares!");

        println!("How many shares do you want to send?");
        let to_send = self.read_u32();
        if to_send >= 0x10000 {
            println!("Nah, you want too much from me.");
            println!("You are now blacklisted!");
            self.trans = false;
            return;
        }

        let balance = self.get_balance();
        let send_event;
        match to_send <= hold {
            false => {
                let mut good: bool = false;
                let to_buy = to_send - hold;
                if to_buy*self.stock_prices[1] <= balance {
                    good = true;
                    println!("You don't have enough shares, so you buy {} shares to send him the shares.", to_buy);
                    let event = StockEvent {action: "buy".to_string(),
                                                      stock_id: 1,
                                                      share: to_buy,
                                                      price: self.stock_prices[1],
                                                      age: self.age};
                    self.events.push(Event::Stock(event));
                }
                if !good {
                    println!("You don't have enough cash to finish the transaction!");
                }
                send_event = StockEvent {action: "send".to_string(),
                                         stock_id: 1,
                                         share: to_send,
                                         price: self.stock_prices[1],
                                         age: self.age};
            }
            true => {
                good = true;
                send_event = StockEvent {action: "send".to_string(),
                                         stock_id: 1,
                                         share: to_send,
                                         price: self.stock_prices[1],
                                         age: self.age};
            }
        }
        if !good {
            println!("You don't have enough shares to send!");
            return;
        }
        self.events.push(Event::Stock(send_event));

        match self.double {
            true => {
                println!("Today is your lucky day!");
                let event = StockEvent {action: "recv".to_string(),
                                                  stock_id: 1,
                                                  share: to_send*2,
                                                  price: self.stock_prices[1],
                                                  age: self.age};
                self.events.push(Event::Stock(event));
            }
            false => {
                println!("There is something wrong with my account, I can't send you the shares, sorry.");
                println!("The shares that you sent me? Sorry, no refund.");
            }
        }

        self.trans = false;
    }

    fn end_game(&self) {
        println!("===========================");
        println!("Game Over");
        self.show_assets();
        println!("");
        println!("Diary        : {}", self.diary);
        process::exit(0);
    }

    fn change_memory(&mut self) {
        println!("Which memory do you want to chagne?");
        let age = self.read_u8();
        if age >= 100 {
            println!("Oh no, the memory becomes unstable, panic!!!");
            self.events = Vec::new();
            self.save_state();
            process::exit(-1);
        }
        let mut smaller_idx= 0;
        let mut larger_idx= self.events.len();
        for idx in 0..self.events.len() {
            let event = &self.events[idx];
            let event_age;
            match event {
                Event::Balance(event)  => {
                    event_age = event.age;
                }
                Event::Stock(event)  => {
                    event_age = event.age;
                }
            }
            if event_age < age {
                smaller_idx = idx;
            } else if event_age > age {
                larger_idx = idx;
                break;
            }
        }
        let events1 = self.events[..smaller_idx+1].to_vec();
        let mut events2 = self.events[larger_idx..].to_vec();
        let age_now = self.age;
        self.age = age;
        self.events = events1;
        self.one_year();
        self.age = age_now;
        self.events.append(&mut events2);
    }

    fn dream(&mut self) {
        println!("Trading meme stocks for the whole life, you turn 100 year-old.");
        if self.promise && self.get_share(4) > 0 {
            println!("You are dying...");
            println!("But somehow you have the obsession of going to the moon.");
            println!("You call in doctors to help you fulfill your dream by altering your memory...");
            self.change_memory();
            self.change_memory();
            println!("Oh no! Your memory becomes unstable, the doctors have to go now!");
        }
        println!("You pass away peacefully. RIP.");
        self.end_game();
    }

    fn rand_gen(&mut self) {
        let mut rng: Pcg64 = Seeder::from(&self.save_file).make_rng();
        let mut array: [u8; 4] = [0; 4];

        loop {
            let mut good = true;
            rng.fill_bytes(&mut array);
            for idx in 0..array.len() {
                array[idx] = (array[idx] % 90) + 6;
            }
            array.sort();
            for idx in 0..(array.len()-1) {
                if array[idx] == array[idx+1] {
                    good = false;
                }
            }
            if good == true {
                break;
            }
        }

        self.accident = array[0];
        self.hype = array[1];
        self.anya = array[2];
        self.dark = array[3];
        self.double = (rng.next_u32() % 2) == 0;
    }

    pub fn login(&mut self) {
        let password;

        println!("Are you a new player? (y/n)");
        let buf = read_line();

        match buf.as_ref() {
            "y" => {
                self.save_file = gen_rand_string(30);
                println!("Password?");
                password = read_line();
                let digest = md5::compute(password);
                self.hash = format!("{:x}", digest);
                self.rand_gen();
                self.save_state();
                println!("Your game save file is at: {}", self.save_file);
            }
            "n" => {
                println!("Where is your save file?");
                let save_file = read_line();
                if save_file.contains(".") {
                    println!("Illegal character detected. Self-destruction program initiated!");
                    process::exit(-1);
                }
                println!("Password?");
                password = read_line();
                let digest = md5::compute(password);
                let hash = format!("{:x}", digest);
                let game = self.load_state(&save_file);

                if hash.ne(&game.hash) {
                    println!("Wrong password!");
                    process::exit(-1);
                }

                *self = game;
                println!("Your game is reloaded, enjoy!");
            }
            _   => {
                println!("I don't understand you!");
                process::exit(-1);
            }
        }

    }

    fn handle_accident(&mut self) {
        println!("A horrible car accident happened.");
        println!("You smell the odor of dead animal and it stays in your memory.");
        println!("To forget the event, you take too many beta-blockers and you lose your memory...");
        self.events = Vec::new();
        self.save_state();
    }

    fn handle_hype(&self) {
        println!("Hold the line and do not sell.");
        println!("GameStop to the moon!");
    }

    fn handle_anya(&mut self) {
        println!("Your wife is sick, she somehow is obsessed with a lighthouse called Anya.");
        let balance = self.get_balance();
        if balance >= 0x1000 {
            println!("To make her happy, you decide to construct a house on a nearby cliff.");
            println!("But she doesn't seem happy...");
            let event = BalanceEvent {action: "sub".to_string(), amount: 0x1000, age: self.age};
            self.events.push(Event::Balance(event));
        } else {
            println!("You want to construct a house on a nearby cliff to make her happy.");
            println!("But you can't afford it.");
            self.promise = false;
        }
    }

    fn handle_dark(&mut self) {
        println!("Yo, I'm kylebot, a hacker from the dark web that you stumbled upon the other day.");
        println!("I heard that you wanted to hack an account very badly.");
        println!("I can help you hack it, in exchange for a liiittle compensation.");
        println!("What do you think? (y/n)");
        let buf = read_line();
        match buf.as_ref() {
            "y" => {
                let balance = self.get_balance();
                if balance < 0x13371337 {
                    println!("You can't afford my service.");
                    println!("Prepare more cash next time!");
                    return;
                }
                println!("Deal!");
                println!("Which accout do you want to hack?");
                let save_file= read_line();
                if save_file.contains(".") || !Path::new(&self.get_save_path(&save_file)).exists() {
                    println!("Are you trying to hack me? No way!");
                    process::exit(-1);
                }
                let game = self.load_state(&save_file);
                println!("There you go. You can read his secret diary now!");
                self.diary = game.diary;
                let event = BalanceEvent {action: "sub".to_string(), amount: 0x13371337, age: self.age};
                self.events.push(Event::Balance(event));
            }
            _ => {
                println!("You don't like the offer?");
                println!("So sad. I'll help others if they want to hack your account then. Good luck.");
                return;
            }
        }
    }

    fn show_assets(&self) {
        println!("Your balance : {}", self.get_balance());
        println!("");
        println!("Stock Shares");
        println!("GameStop     : {}", self.get_share(1));
        println!("AMC          : {}", self.get_share(2));
        println!("BlackBerry   : {}", self.get_share(3));
        println!("ForRiver     : {}", self.get_share(4));
    }

    fn one_year(&mut self) {
        println!("================================");
        if self.age == self.accident {
            self.handle_accident();
        } else if self.age == self.hype {
            self.handle_hype();
        } else if self.age == self.anya {
            self.handle_anya();
        } else if self.age == self.dark {
            self.handle_dark();
        } else if self.age == 100 {
            self.dream();
        } else {
            let choice: i8 = self.action_menu();
            if choice < 0 {return;}
            match choice {
                1 => {self.pass_time();}
                2 => {self.write_diary();}
                3 => {self.read_diary();}
                4 => {self.carnival();}
                5 => {self.part_time();}
                6 => {self.stock();}
                7 => {self.transaction();}
                126 => {self.show_assets();}
                127 => {
                    self.save_state();
                    process::exit(0);
                }
                _ => {
                    println!("Unexpected Value");
                    process::exit(-1);
                }
            }
        }
        self.age += 1;
    }

    pub fn start(&mut self) {
        loop {
            self.one_year();
        }
    }
}
