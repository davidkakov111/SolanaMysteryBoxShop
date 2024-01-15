"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var web3_js_1 = require("@solana/web3.js");
var js_1 = require("@metaplex-foundation/js");
var bs58 = require("bs58");
var uint8ArrayPrivateKey = bs58.decode("3ahvEw68DHexJjpY5J4NnXATA72iE8hDjuN6bi8TpGxDbWqKTt3cC3RiESyE5A1KBq8pA9o3BJikpMF5ynMnS3hW");
var WALLET = web3_js_1.Keypair.fromSecretKey(uint8ArrayPrivateKey);
var METAPLEX = js_1.Metaplex.make(new web3_js_1.Connection('https://api.devnet.solana.com'))
    .use((0, js_1.keypairIdentity)(WALLET));
var CONFIG = {
    uri: 'https://arweave.net/d_UMa4GP_utfPOFJgwqXp_NmzT_yy261LMl014G5G9w',
    imgName: 'DAVID',
    sellerFeeBasisPoints: 300, //200 bp = 3%
    symbol: 'DaV',
    creators: [
        { address: WALLET.publicKey, share: 100 }
    ]
};
function mintNft(metadataUri, name, sellerFee, symbol, creators) {
    return __awaiter(this, void 0, void 0, function () {
        var metaplex, nft, error_1, errorMessage, parts, lastPart, nftaddress;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    metaplex = METAPLEX.use((0, js_1.keypairIdentity)(WALLET));
                    return [4 /*yield*/, metaplex.nfts().create({
                            uri: metadataUri,
                            name: name,
                            sellerFeeBasisPoints: sellerFee,
                            symbol: symbol,
                            creators: creators,
                            isMutable: false,
                            maxSupply: (0, js_1.toBigNumber)(1),
                        })];
                case 1:
                    nft = (_a.sent()).nft;
                    console.log(nft.address.toBase58(), "!?!!?!?!?!?!?");
                    return [3 /*break*/, 3];
                case 2:
                    error_1 = _a.sent();
                    // This is an internal sdk error.
                    if (error_1 instanceof js_1.AccountNotFoundError) {
                        errorMessage = error_1.message;
                        parts = errorMessage.split('[');
                        lastPart = parts[parts.length - 1];
                        nftaddress = lastPart.split(']')[0];
                        console.log(nftaddress);
                    }
                    else {
                        // Log other errors
                        console.error("Unexpected error:", error_1);
                    }
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    });
}
mintNft(CONFIG.uri, CONFIG.imgName, CONFIG.sellerFeeBasisPoints, CONFIG.symbol, CONFIG.creators);
