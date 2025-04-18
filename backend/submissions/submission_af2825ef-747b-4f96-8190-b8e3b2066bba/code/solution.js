const readline = require('readline');

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    function addNumbers(a, b) {
        console.log(Number(a) + Number(b) );
    }

    rl.on('line', (input) => {
        const [a, b] = input.trim().split(" ");
        addNumbers(a, b);
        rl.close();
    });