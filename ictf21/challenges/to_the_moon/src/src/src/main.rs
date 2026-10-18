mod game;

fn greeting() {
    println!("$$\\  $$$$$$\\ $$$$$$$$\\ $$$$$$$$\\        $$$$$$\\   $$$$$$\\   $$$$$$\\    $$\\   ");
    println!("\\__|$$  __$$\\\\__$$  __|$$  _____|      $$  __$$\\ $$$ __$$\\ $$  __$$\\ $$$$ |  ");
    println!("$$\\ $$ /  \\__|  $$ |   $$ |            \\__/  $$ |$$$$\\ $$ |\\__/  $$ |\\_$$ |  ");
    println!("$$ |$$ |        $$ |   $$$$$\\           $$$$$$  |$$\\$$\\$$ | $$$$$$  |  $$ |  ");
    println!("$$ |$$ |        $$ |   $$  __|         $$  ____/ $$ \\$$$$ |$$  ____/   $$ |  ");
    println!("$$ |$$ |  $$\\   $$ |   $$ |            $$ |      $$ |\\$$$ |$$ |        $$ |  ");
    println!("$$ |\\$$$$$$  |  $$ |   $$ |            $$$$$$$$\\ \\$$$$$$  /$$$$$$$$\\ $$$$$$\\ ");
    println!("\\__| \\______/   \\__|   \\__|            \\________| \\______/ \\________|\\______|");
    println!("");
    println!("Welcome to iCTF 2021 meme stock trading simulator, you can trade meme stocks here for your whole life!");
}

fn main() {
    greeting();
    let mut game = game::Game::new();
    game.login();
    game.start();
}