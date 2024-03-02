let mysql = require('mysql');

let connection = mysql.createConnection({
    host: '116043724',
    user: 'JustineG57',
    password: 'J7fuy589*',
    database: 'project.db'

});

connection.connect(function(err) {
    if (err) {
        return console.error('error: ' + err.message);
    }

    console.log('Connected to the MySQL server.');
})







var mysql = require('mysql');

        var con = mysql.createConnection({
            sever: "localhost",
            user: "yourusername",
            password: "yourpassword",
            database: "project"
        });

        con.connect(function(err) {
            if (err) throw err;
            var sql = "INSERT INTO book (title, author, ISBN, pages) VALUES (?, ?, ?, ?), title, author, isbn, pages";
            con.query(sql, function (err, result) {
                if (err) throw err;
                console.log("1 record inserted");
            });
        });




        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");



        var request = new XMLHttpRequest();
        request.open('POST', '/listofbooks', true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        request.onreadystatechange =


        request.send('title=' + title, 'author=' + author, 'isbn=' + isbn, 'pages=' + pages);