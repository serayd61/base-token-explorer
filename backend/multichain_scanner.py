# backend/multichain_scanner.py - Güncellenmiş Superchain Scanner
from datetime import datetime
from web3 import Web3
import os
import json
import requests
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ChainConfig:
    """Configuration for different blockchain networks"""
    name: str
    rpc_url: str
    chain_id: int
    weth_address: str
    uniswap_v2_factory: str
    uniswap_v3_factory: str
    block_time: float
    is_op_stack: bool = False
    explorer_url: str = ""

class MultiChainTokenScanner:
    def __init__(self):
        # Chain configurations
        self.chains = {
            "ethereum": ChainConfig(
                name="ethereum",
                rpc_url="https://ethereum.publicnode.com",
                chain_id=1,
                weth_address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                uniswap_v2_factory="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
                uniswap_v3_factory="0x1F98431c8aD98523631AE4a59f267346ea31F984",
                block_time=12.0,
                is_op_stack=False,
                explorer_url="https://etherscan.io"
            ),
            "base": ChainConfig(
                name="base",
                rpc_url="https://mainnet.base.org",
                chain_id=8453,
                weth_address="0x4200000000000000000000000000000000000006",
                uniswap_v2_factory="0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6",
                uniswap_v3_factory="0x33128a8fC17869897dcE68Ed026d694621f6FDfD",
                block_time=2.0,
                is_op_stack=True,
                explorer_url="https://basescan.org"
            ),
            "optimism": ChainConfig(
                name="optimism",
                rpc_url="https://mainnet.optimism.io",
                chain_id=10,
                weth_address="0x4200000000000000000000000000000000000006",
                uniswap_v2_factory="0x0c4c792E6E01f6B8c2C44c66bB69f4C2c2039b26",  # Alternative DEX
                uniswap_v3_factory="0x1F98431c8aD98523631AE4a59f267346ea31F984",
                block_time=2.0,
                is_op_stack=True,
                explorer_url="https://optimistic.etherscan.io"
            ),
            "mode": ChainConfig(
                name="mode",
                rpc_url="https://mainnet.mode.network",
                chain_id=34443,
                weth_address="0x4200000000000000000000000000000000000006",
                uniswap_v2_factory="0x5C7BC93471A28D5a29C6052a8E4B238009de6ac6",  # Mode specific
                uniswap_v3_factory="0x6BDED42c6DA8FBf0d2bA55B2fa120C5e0c8D7891",  # Mode specific
                block_time=2.0,
                is_op_stack=True,
                explorer_url="https://explorer.mode.network"
            ),
            "zora": ChainConfig(
                name="zora",
                rpc_url="https://rpc.zora.energy",
                chain_id=7777777,
                weth_address="0x4200000000000000000000000000000000000006",
                uniswap_v2_factory="0x0000000000000000000000000000000000000000",  # To be updated
                uniswap_v3_factory="0x0000000000000000000000000000000000000000",  # To be updated
                block_time=2.0,
                is_op_stack=True,
                explorer_url="https://explorer.zora.energy"
            ),
            "fraxtal": ChainConfig(
                name="fraxtal",
                rpc_url="https://rpc.frax.com",
                chain_id=252,
                weth_address="0x4200000000000000000000000000000000000006",
                uniswap_v2_factory="0x0000000000000000000000000000000000000000",  # To be updated
                uniswap_v3_factory="0x0000000000000000000000000000000000000000",  # To be updated
                block_time=2.0,
                is_op_stack=True,
                explorer_url="https://fraxscan.com"
            ),
            "world": ChainConfig(
                name="world",
                rpc_url="https://worldchain-mainnet.g.alchemy.com/public",
                chain_id=480,
                weth_address="0x4200000000000000000000000000000000000006",
                uniswap_v2_factory="0x0000000000000000000000000000000000000000",  # To be updated
                uniswap_v3_factory="0x0000000000000000000000000000000000000000",  # To be updated
                block_time=2.0,
                is_op_stack=True,
                explorer_url="https://worldscan.org"
            ),
            "lisk": ChainConfig(
                name="lisk",
                rpc_url="https://rpc.api.lisk.com",
                chain_id=1135,
                weth_address="0x4200000000000000000000000000000000000006",
                uniswap_v2_factory="0x0000000000000000000000000000000000000000",  # To be updated
                uniswap_v3_factory="0x0000000000000000000000000000000000000000",  # To be updated
                block_time=2.0,
                is_op_stack=True,
                explorer_url="https://blockscout.lisk.com"
            ),
            "arbitrum": ChainConfig(
                name="arbitrum",
                rpc_url="https://arbitrum.publicnode.com",
                chain_id=42161,
                weth_address="0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
                uniswap_v2_factory="0xf1D7CC64Fb4452F05c498126312eBE29f30Fbcf9",
                uniswap_v3_factory="0x1F98431c8aD98523631AE4a59f267346ea31F984",
                block_time=0.25,
                is_op_stack=False,
                explorer_url="https://arbiscan.io"
            ),
            "polygon": ChainConfig(
                name="polygon",
                rpc_url="https://polygon.llamarpc.com",
                chain_id=137,
                weth_address="0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",  # WMATIC
                uniswap_v2_factory="0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32",  # QuickSwap
                uniswap_v3_factory="0x1F98431c8aD98523631AE4a59f267346ea31F984",
                block_time=2.0,
                is_op_stack=False,
                explorer_url="https://polygonscan.com"
            )
        }
        
        # Current chain setup
        self.current_chain = None
        self.w3 = None
        
        # ABIs (same for all chains)
        self.FACTORY_V2_ABI = [{
            "constant": True,
            "inputs": [
                {"internalType": "address", "name": "tokenA", "type": "address"},
                {"internalType": "address", "name": "tokenB", "type": "address"}
            ],
            "name": "getPair",
            "outputs": [{"internalType": "address", "name": "pair", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        }]
        
        self.FACTORY_V3_ABI = [{
            "constant": True,
            "inputs": [
                {"internalType": "address", "name": "tokenA", "type": "address"},
                {"internalType": "address", "name": "tokenB", "type": "address"},
                {"internalType": "uint24", "name": "fee", "type": "uint24"}
            ],
            "name": "getPool",
            "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        }]
        
        # V3 fee tiers
        self.V3_FEES = [500, 3000, 10000]  # 0.05%, 0.3%, 1%
        
        # Rate limiting
        self.last_api_call = 0
        self.api_delay = 1  # seconds

    def get_op_stack_chains(self) -> List[str]:
        """Get list of OP Stack chains"""
        return [name for name, config in self.chains.items() if config.is_op_stack]

    def get_superchain_summary(self) -> Dict:
        """Generate Superchain ecosystem summary"""
        op_chains = self.get_op_stack_chains()
        return {
            "total_op_chains": len(op_chains),
            "op_chains": op_chains,
            "non_op_chains": [name for name, config in self.chains.items() if not config.is_op_stack]
        }

    def set_chain(self, chain_name: str) -> bool:
        """Switch to a different blockchain network"""
        if chain_name not in self.chains:
            print(f"❌ Unsupported chain: {chain_name}")
            print(f"Available chains: {list(self.chains.keys())}")
            return False
        
        try:
            self.current_chain = self.chains[chain_name]
            self.w3 = Web3(Web3.HTTPProvider(self.current_chain.rpc_url))
            
            if self.check_rpc_connection():
                op_status = "🟢 OP Stack" if self.current_chain.is_op_stack else "🔵 Non-OP"
                print(f"✅ Switched to {chain_name.upper()} network ({op_status})")
                return True
            else:
                print(f"❌ Failed to connect to {chain_name}")
                return False
        except Exception as e:
            print(f"❌ Error switching to {chain_name}: {e}")
            return False

    def check_rpc_connection(self) -> bool:
        """Test RPC connection"""
        try:
            latest_block = self.w3.eth.block_number
            chain_id = self.w3.eth.chain_id
            print(f"✅ RPC connection successful. Latest block: {latest_block}, Chain ID: {chain_id}")
            return True
        except Exception as e:
            print(f"❌ RPC connection error: {e}")
            return False

    def get_contract_address_from_tx(self, tx) -> Optional[str]:
        """Extract contract address from transaction"""
        try:
            if tx.to is None:
                receipt = self.w3.eth.get_transaction_receipt(tx.hash)
                if receipt.contractAddress:
                    return Web3.to_checksum_address(receipt.contractAddress)
            return None
        except Exception as e:
            print(f"⚠️ Could not get contract address: {e}")
            return None

    def check_uniswap_v2_lp(self, token_address: str) -> bool:
        """Check if LP exists on Uniswap V2"""
        try:
            if self.current_chain.uniswap_v2_factory == "0x0000000000000000000000000000000000000000":
                return False  # No V2 factory configured
                
            token_address = Web3.to_checksum_address(token_address)
            factory_address = Web3.to_checksum_address(self.current_chain.uniswap_v2_factory)
            factory = self.w3.eth.contract(address=factory_address, abi=self.FACTORY_V2_ABI)
            pair = factory.functions.getPair(token_address, self.current_chain.weth_address).call()
            return int(pair, 16) != 0
        except Exception as e:
            print(f"⚠️ V2 LP check error: {e}")
            return False

    def check_uniswap_v3_lp(self, token_address: str) -> bool:
        """Check if LP exists on Uniswap V3"""
        try:
            if self.current_chain.uniswap_v3_factory == "0x0000000000000000000000000000000000000000":
                return False  # No V3 factory configured
                
            token_address = Web3.to_checksum_address(token_address)
            factory_address = Web3.to_checksum_address(self.current_chain.uniswap_v3_factory)
            factory = self.w3.eth.contract(address=factory_address, abi=self.FACTORY_V3_ABI)
            
            for fee in self.V3_FEES:
                try:
                    pool = factory.functions.getPool(token_address, self.current_chain.weth_address, fee).call()
                    if int(pool, 16) != 0:
                        return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"⚠️ V3 LP check error: {e}")
            return False

    def check_lp_exists(self, token_address: str) -> Dict[str, any]:
        """Check LP status on both V2 and V3"""
        if not token_address or not self.current_chain:
            return {"v2": False, "v3": False, "status": "NO_ADDRESS"}
        
        try:
            v2_exists = self.check_uniswap_v2_lp(token_address)
            v3_exists = self.check_uniswap_v3_lp(token_address)
            
            status = "YES" if (v2_exists or v3_exists) else "NO"
                
            return {
                "v2": v2_exists,
                "v3": v3_exists,
                "status": status
            }
        except Exception as e:
            print(f"⚠️ LP check error for {token_address}: {e}")
            return {"v2": False, "v3": False, "status": "ERROR"}

    def fetch_dexscreener_data(self, token_address: str) -> Dict[str, any]:
        """Fetch token data from DexScreener"""
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_api_call < self.api_delay:
                time.sleep(self.api_delay - (current_time - self.last_api_call))
            
            # DexScreener chain mapping
            chain_mapping = {
                "ethereum": "ethereum",
                "base": "base", 
                "optimism": "optimism",
                "mode": "mode",
                "zora": "zora",
                "fraxtal": "fraxtal",
                "world": "worldchain",
                "lisk": "lisk",
                "arbitrum": "arbitrum",
                "polygon": "polygon"
            }
            
            chain_name = chain_mapping.get(self.current_chain.name, self.current_chain.name)
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            
            response = requests.get(url, timeout=10)
            self.last_api_call = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if "pairs" in data and data["pairs"]:
                    # Filter pairs for current chain
                    chain_pairs = [p for p in data["pairs"] if p.get("chainId") == str(self.current_chain.chain_id)]
                    if chain_pairs:
                        pair = chain_pairs[0]
                        return {
                            "price_usd": pair.get("priceUsd", "0"),
                            "volume_24h": pair.get("volume", {}).get("h24", "0"),
                            "liquidity": pair.get("liquidity", {}).get("usd", "0"),
                            "pair_address": pair.get("pairAddress", ""),
                            "dex": pair.get("dexId", "unknown"),
                            "chain": chain_name
                        }
            return {}
        except Exception as e:
            print(f"⚠️ DexScreener API error: {e}")
            return {}

    def get_token_metadata(self, token_address: str) -> Dict[str, any]:
        """Get basic token metadata (name, symbol, decimals)"""
        try:
            erc20_abi = [
                {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
            ]
            
            contract = self.w3.eth.contract(address=token_address, abi=erc20_abi)
            
            try:
                name = contract.functions.name().call()
            except:
                name = "Unknown"
            
            try:
                symbol = contract.functions.symbol().call()
            except:
                symbol = "UNKNOWN"
            
            try:
                decimals = contract.functions.decimals().call()
            except:
                decimals = 18
            
            try:
                total_supply = contract.functions.totalSupply().call()
                total_supply = total_supply / (10 ** decimals)
            except:
                total_supply = 0
            
            return {
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "total_supply": total_supply
            }
        except Exception as e:
            print(f"⚠️ Token metadata error: {e}")
            return {"name": "Unknown", "symbol": "UNKNOWN", "decimals": 18, "total_supply": 0}

    def scan_recent_blocks(self, block_count: int = 50) -> List[Dict]:
        """Scan last N blocks for new contract deployments"""
        if not self.current_chain or not self.check_rpc_connection():
            return []
        
        latest_block = self.w3.eth.block_number
        start_block = latest_block - block_count
        results = []
        
        chain_icon = "🟢" if self.current_chain.is_op_stack else "🔵"
        print(f"🔍 Scanning {self.current_chain.name.upper()} blocks {start_block} to {latest_block}... {chain_icon}")
        
        for block_num in range(start_block, latest_block + 1):
            try:
                print(f"📦 Processing block {block_num}...")
                block = self.w3.eth.get_block(block_num, full_transactions=True)
                
                for tx in block.transactions:
                    contract_address = self.get_contract_address_from_tx(tx)
                    
                    if contract_address:
                        print(f"🆕 New contract found: {contract_address}")
                        
                        # Get token metadata
                        metadata = self.get_token_metadata(contract_address)
                        
                        # Check LP status
                        lp_info = self.check_lp_exists(contract_address)
                        
                        # Fetch DexScreener data if LP exists
                        dex_data = {}
                        if lp_info["status"] == "YES":
                            dex_data = self.fetch_dexscreener_data(contract_address)
                        
                        result = {
                            "chain": self.current_chain.name,
                            "chain_id": self.current_chain.chain_id,
                            "is_op_stack": self.current_chain.is_op_stack,
                            "block": block_num,
                            "hash": tx.hash.hex(),
                            "deployer": tx["from"],
                            "contract_address": contract_address,
                            "timestamp": datetime.utcfromtimestamp(block.timestamp).isoformat(),
                            "metadata": metadata,
                            "lp_info": lp_info,
                            "dex_data": dex_data,
                            "explorer_url": f"{self.current_chain.explorer_url}/address/{contract_address}"
                        }
                        
                        results.append(result)
                        print(f"✅ Contract saved: {metadata['symbol']} - LP={lp_info['status']}")
                        
            except Exception as e:
                print(f"⚠️ Block {block_num} error: {e}")
                continue
        
        return results

    def scan_op_stack_chains(self, block_count: int = 20) -> Dict[str, List[Dict]]:
        """Scan only OP Stack chains"""
        op_chains = self.get_op_stack_chains()
        print(f"\n🟢 Starting OP Stack Superchain scan for: {', '.join(op_chains)}")
        
        all_results = {}
        for chain_name in op_chains:
            print(f"\n🌐 Starting scan for {chain_name.upper()}...")
            
            if self.set_chain(chain_name):
                results = self.scan_recent_blocks(block_count)
                all_results[chain_name] = results
                print(f"✅ {chain_name.upper()} scan completed: {len(results)} contracts found")
            else:
                print(f"❌ Skipping {chain_name} due to connection issues")
                all_results[chain_name] = []
        
        return all_results

    def scan_multiple_chains(self, chains: List[str], block_count: int = 20) -> Dict[str, List[Dict]]:
        """Scan multiple chains and return combined results"""
        all_results = {}
        
        for chain_name in chains:
            print(f"\n🌐 Starting scan for {chain_name.upper()}...")
            
            if self.set_chain(chain_name):
                results = self.scan_recent_blocks(block_count)
                all_results[chain_name] = results
                print(f"✅ {chain_name.upper()} scan completed: {len(results)} contracts found")
            else:
                print(f"❌ Skipping {chain_name} due to connection issues")
                all_results[chain_name] = []
        
        return all_results

    def save_results(self, results: Dict[str, List[Dict]], filename: str = "superchain_tokens_scan.json"):
        """Save results to file"""
        output_path = os.path.join("public", filename)
        os.makedirs("public", exist_ok=True)
        
        # Flatten results for easier analysis
        flattened_results = []
        for chain, chain_results in results.items():
            flattened_results.extend(chain_results)
        
        # Add superchain summary
        superchain_info = self.get_superchain_summary()
        
        # Save comprehensive format
        with open(output_path, "w") as f:
            json.dump({
                "scan_time": datetime.now().isoformat(),
                "superchain_info": superchain_info,
                "chains": results,
                "flattened": flattened_results,
                "stats": {
                    "total_contracts": len(flattened_results),
                    "op_stack_contracts": len([r for r in flattened_results if r.get("is_op_stack", False)]),
                    "chains_scanned": list(results.keys())
                }
            }, f, indent=2)
        
        total_contracts = len(flattened_results)
        op_contracts = len([r for r in flattened_results if r.get("is_op_stack", False)])
        print(f"✅ {total_contracts} total results saved to: {output_path}")
        print(f"🟢 {op_contracts} OP Stack contracts found")

    def generate_superchain_summary(self, results: Dict[str, List[Dict]]):
        """Generate comprehensive Superchain summary report"""
        print(f"\n📊 SUPERCHAIN ECOSYSTEM SCAN SUMMARY:")
        print("=" * 60)
        
        total_contracts = 0
        total_lp_contracts = 0
        op_stack_contracts = 0
        chain_stats = {}
        
        for chain, chain_results in results.items():
            contracts = len(chain_results)
            lp_contracts = len([r for r in chain_results if r["lp_info"]["status"] == "YES"])
            is_op_stack = self.chains[chain].is_op_stack
            
            total_contracts += contracts
            total_lp_contracts += lp_contracts
            if is_op_stack:
                op_stack_contracts += contracts
            
            chain_stats[chain] = {
                "contracts": contracts,
                "lp_contracts": lp_contracts,
                "success_rate": (lp_contracts/contracts*100) if contracts > 0 else 0,
                "is_op_stack": is_op_stack
            }
            
            chain_icon = "🟢" if is_op_stack else "🔵"
            stack_label = "OP Stack" if is_op_stack else "Non-OP"
            print(f"\n{chain_icon} {chain.upper()} ({stack_label}):")
            print(f"   Contracts deployed: {contracts}")
            print(f"   With LP: {lp_contracts}")
            print(f"   Success rate: {chain_stats[chain]['success_rate']:.1f}%")
        
        print(f"\n🌐 SUPERCHAIN TOTALS:")
        print(f"Total contracts: {total_contracts}")
        print(f"🟢 OP Stack contracts: {op_stack_contracts}")
        print(f"🔵 Non-OP contracts: {total_contracts - op_stack_contracts}")
        print(f"Total with LP: {total_lp_contracts}")
        print(f"Overall success rate: {(total_lp_contracts/total_contracts*100):.1f}%" if total_contracts > 0 else "Overall success rate: 0%")
        
        # OP Stack specific analysis
        op_chains = [chain for chain, stats in chain_stats.items() if stats["is_op_stack"]]
        if op_chains:
            print(f"\n🟢 OP STACK ECOSYSTEM ANALYSIS:")
            print(f"Chains scanned: {', '.join(op_chains)}")
            best_op_chain = max([c for c in op_chains if chain_stats[c]["contracts"] > 0], 
                              key=lambda x: chain_stats[x]["success_rate"], default=None)
            if best_op_chain:
                print(f"🏆 Best performing OP chain: {best_op_chain.upper()} ({chain_stats[best_op_chain]['success_rate']:.1f}%)")

def main():
    scanner = MultiChainTokenScanner()
    
    print("🚀 Starting Superchain Token Scanner...")
    print("🟢 OP Stack Chains:", scanner.get_op_stack_chains())
    
    # Option 1: Scan only OP Stack chains (recommended for grant application)
    print("\n1️⃣ Scanning OP Stack Superchain...")
    op_results = scanner.scan_op_stack_chains(block_count=10)
    scanner.save_results(op_results, "superchain_tokens.json")
    scanner.generate_superchain_summary(op_results)
    
    # Option 2: Scan all chains for comparison
    print("\n2️⃣ Scanning All Chains for comparison...")
    all_chains = ["base", "optimism", "mode", "ethereum", "arbitrum"]  # Start with core chains
    all_results = scanner.scan_multiple_chains(all_chains, block_count=5)
    scanner.save_results(all_results, "multichain_comparison.json")
    scanner.generate_superchain_summary(all_results)

if __name__ == "__main__":
    main()