const hre = require("hardhat");

async function main() {
  console.log("Deploying AdoptIQ contracts...");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "ETH");

  const BillingContract = await hre.ethers.getContractFactory("BillingContract");
  const billingContract = await BillingContract.deploy();
  await billingContract.waitForDeployment();
  const billingAddress = await billingContract.getAddress();
  console.log("BillingContract deployed to:", billingAddress);

  const CertificateRegistry = await hre.ethers.getContractFactory("CertificateRegistry");
  const certificateRegistry = await CertificateRegistry.deploy();
  await certificateRegistry.waitForDeployment();
  const registryAddress = await certificateRegistry.getAddress();
  console.log("CertificateRegistry deployed to:", registryAddress);

  const usdcAddress = process.env.USDC_ADDRESS || "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48";
  console.log("Setting supported token (USDC):", usdcAddress);
  await billingContract.setSupportedToken(usdcAddress, true);
  console.log("USDC support enabled");

  console.log("\nDeployment Summary:");
  console.log("===================");
  console.log("BillingContract:", billingAddress);
  console.log("CertificateRegistry:", registryAddress);
  console.log("\nAdd these addresses to your .env file:");
  console.log(`BILLING_CONTRACT_ADDRESS=${billingAddress}`);
  console.log(`CERTIFICATE_REGISTRY_ADDRESS=${registryAddress}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
