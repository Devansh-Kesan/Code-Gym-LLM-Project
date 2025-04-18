
const { spawnSync } = require('child_process');
const path = require('path');

describe('Test hidden_0', () => {
    it('should match expected output', () => {
        const input = '100 100\n';
        const expected = '200';

        const result = spawnSync('node', [path.join('/code', 'solution.js')], { 
            input, 
            timeout: 5000, 
            encoding: 'utf-8' 
        });

        if (result.error) {
            if (result.error.code === 'ETIMEDOUT') {
                throw new Error('Time Limit Exceeded');
            }
            throw result.error;
        }

        if (result.status !== 0) {
            throw new Error(`Process exited with code ${result.status}`);
        }

        console.log("Test Result:");
        console.log(JSON.stringify(result, null, 2));

        const output = result.stdout.trim().split('\n').pop();
        expect(output).toBe(expected);
    });
});
