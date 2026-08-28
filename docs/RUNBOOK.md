# Deploy and rollback

Build by immutable digest. Deploy only the inactive slot, require `/health/ready`,
then switch the gateway by a graceful reload and drain the old slot. Workers stop
new claims on SIGTERM and finish current leases. Never run a migration here.
Rollback switches only runtime to its prior manifest digest; no transport restart.
