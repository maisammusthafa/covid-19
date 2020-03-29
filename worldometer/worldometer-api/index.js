const fs = require('fs')
const covid = require('covid19-api')

const successCallback = (result) => {
    const json = JSON.stringify(result[0], null, 2)

    fs.writeFile('source_data.json', json, 'utf8', (error) => {
        if (error) {
            throw error
        }
    });
}

covid.getReports().then(successCallback)
