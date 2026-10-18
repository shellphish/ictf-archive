const {scrypt, pbkdf2} = require('crypto');
const {ec: EC} = require('elliptic');
const s256 = new EC('secp256k1');
const keccak = require('keccak');
const ethers = require('ethers');

function keccak256(s) {
    return keccak('keccak256').update(s).digest();
}

function keyToEthereum(key) {
  let pubkey = Buffer.from(s256.keyFromPrivate(key).getPublic(false, 'hex'), 'hex');
  return {
    private: key.toString('hex'),
    public: '0x' + keccak256(pubkey.slice(1)).slice(12).toString('hex')
  };
}

function warpwallet(password, salt, power, hashSuffix, callback) {
  let password_buffer = Buffer.from(password, 'utf-8');
  let salt_buffer = Buffer.from(salt, 'utf-8');
  let x1 = Buffer.alloc(1, hashSuffix);
  let x2 = Buffer.alloc(1, hashSuffix + 1);

  const options = {
    N: Math.pow(2, power),
    r: 8,
    p: 1,
    maxmem: 1024 * 1024 * 1024
  };
  scrypt(Buffer.concat([password_buffer, x1]), Buffer.concat([salt_buffer, x1]), 32, options, (err, key1) => {
    if(key1) {
      pbkdf2(Buffer.concat([password_buffer, x2]), Buffer.concat([salt_buffer, x2]), Math.pow(2, 16) /* iterations */, 32 /* keylen */, 'sha256' /* digest */, function(err, key2) {
        if (err) {
          console.error(err);
          process.exit(1);
        }
        for (let i = 0; i < 32; i++) {
          key2[i] = key2[i] ^ key1[i];
        }
        callback(1, key2);
      });
      return;
    }
    callback(err, null);
  });
}

function generateWallet(passphrase, salt, callback) {
  warpwallet(passphrase, salt, 18 /* power */, 2 /* hashSuffix */, function(progress, result) {
    if(result) {
      let wallet = keyToEthereum(result)
      callback(1, wallet)
    } else {
      callback(progress, null);
    }
  });
}


generateWallet(process.argv[2], 'H4KK0RZ!!', (_, key) => {
  const pubkey = ethers.utils.getAddress(key['public']);
  console.log(pubkey + ' ' + key['private']);
});


