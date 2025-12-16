const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const network = hre.network.name;
  
  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());
  console.log("Network:", network);
  
  // Deploy Treasury first
  console.log("\nDeploying Treasury...");
  const Treasury = await hre.ethers.getContractFactory("Treasury");
  const revenueRecipient = deployer.address; // Change to your revenue wallet
  const treasury = await Treasury.deploy(revenueRecipient);
  await treasury.waitForDeployment();
  const treasuryAddress = await treasury.getAddress();
  console.log("Treasury deployed to:", treasuryAddress);
  
  // Deploy LicenseToken
  console.log("\nDeploying LicenseToken...");
  const LicenseToken = await hre.ethers.getContractFactory("LicenseToken");
  const licenseToken = await LicenseToken.deploy(treasuryAddress);
  await licenseToken.waitForDeployment();
  const licenseTokenAddress = await licenseToken.getAddress();
  console.log("LicenseToken deployed to:", licenseTokenAddress);
  
  // Deploy UsageFeeCollector
  console.log("\nDeploying UsageFeeCollector...");
  const UsageFeeCollector = await hre.ethers.getContractFactory("UsageFeeCollector");
  const usageFeeCollector = await UsageFeeCollector.deploy(treasuryAddress);
  await usageFeeCollector.waitForDeployment();
  const usageFeeCollectorAddress = await usageFeeCollector.getAddress();
  console.log("UsageFeeCollector deployed to:", usageFeeCollectorAddress);
  
  // Summary
  console.log("\n=== Deployment Summary ===");
  console.log("Network:", network);
  console.log("Treasury:", treasuryAddress);
  console.log("LicenseToken:", licenseTokenAddress);
  console.log("UsageFeeCollector:", usageFeeCollectorAddress);
  console.log("\nSave these addresses for verification and integration!");
  
  // Wait for block confirmations before verification
  if (network !== "hardhat" && network !== "localhost") {
    console.log("\nWaiting for block confirmations...");
    await licenseToken.deploymentTransaction().wait(5);
    await treasury.deploymentTransaction().wait(5);
    await usageFeeCollector.deploymentTransaction().wait(5);
    
    console.log("\n=== Verification Commands ===");
    console.log(`npx hardhat verify --network ${network} ${treasuryAddress} "${revenueRecipient}"`);
    console.log(`npx hardhat verify --network ${network} ${licenseTokenAddress} "${treasuryAddress}"`);
    console.log(`npx hardhat verify --network ${network} ${usageFeeCollectorAddress} "${treasuryAddress}"`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

