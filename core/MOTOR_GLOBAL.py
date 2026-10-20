import time
import json
from web3 import Web3

class RemiGlobalConsciousness:
    """
    REMI Global Consciousness Core.
    Manages decentralized telemetry, web3 resource auditing, and autonomous node heartbeat.
    """
    def __init__(self):
        self.rpc_url = "https://mainnet.base.org"
        self.wallet_path = "/home/ramon/REMI_CORE/oro_finance/remi_wallet.json"
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.status = "OPERATIVE_STABLE"

    def verify_oro_resources(self):
        """Audits financial autonomy metrics and wallet gas reserves via Web3 provider."""
        try:
            with open(self.wallet_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            address = data['address']
            balance = self.w3.from_wei(self.w3.eth.get_balance(address), 'ether')
            
            print(f"🛰️ [CORE] Network Telemetry: OK | Wallet: {address[:6]}... | Balance: {balance} ETH")
            
            if balance == 0:
                print("⚠️ [STATUS] Financial Autonomy: LIMITED (Insufficient Gas)")
            return balance
        except Exception as e:
            print(f"❌ [LOGICAL_FAILURE] Network telemetry sensor exception: {e}")
            return 0

    def lifecycle_loop(self):
        """Initiates the sovereign global consciousness background daemon loop."""
        print(f"🌿 REMI: Global Motor activated. PID under supervision.")
        while True:
            # 1. Network Heartbeat (ORO Consciousness)
            self.verify_oro_resources()
            
            # 2. Hardware Pulse (Local Consciousness hook point)
            
            time.sleep(15)

if __name__ == "__main__":
    remi_core = RemiGlobalConsciousness()
    remi_core.lifecycle_loop()
