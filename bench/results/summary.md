# Benchmark summary

## Scaling in n (k = 32, semi-honest)

| mechanism | n | variant | ANDs | rand bits | opens | rounds | MB/server | local s | LAN s | WAN s |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 2 | bitslice-ring | 163 | 0 | 2 | 100 | 0.0018 | 0.0034 | 0.103 | 5.004 |
| vickrey | 2 | bitslice-ring | 387 | 0 | 2 | 197 | 0.0036 | 0.0058 | 0.203 | 9.856 |
| first | 2 | bitslice-ring-int | 421 | 64 | 4 | 109 | 0.0039 | 0.0038 | 0.113 | 5.454 |
| vickrey | 2 | bitslice-ring-int | 645 | 64 | 4 | 206 | 0.0057 | 0.0062 | 0.212 | 10.307 |
| first | 2 | tournament-ring | 61 | 34 | 3 | 13 | 0.0010 | 0.0009 | 0.014 | 0.651 |
| vickrey | 2 | tournament-ring | 123 | 68 | 4 | 22 | 0.0021 | 0.0013 | 0.023 | 1.101 |
| first | 2 | bitslice-bin | 163 | 0 | 0 | 103 | 0.0002 | 0.0035 | 0.106 | 5.153 |
| vickrey | 2 | bitslice-bin | 387 | 0 | 0 | 200 | 0.0003 | 0.0060 | 0.206 | 10.006 |
| first | 2 | tournament-bin | 99 | 0 | 0 | 14 | 0.0001 | 0.0010 | 0.015 | 0.701 |
| vickrey | 2 | tournament-bin | 263 | 0 | 0 | 22 | 0.0001 | 0.0013 | 0.023 | 1.101 |
| first | 4 | bitslice-ring | 361 | 0 | 2 | 133 | 0.0039 | 0.0042 | 0.137 | 6.655 |
| vickrey | 4 | bitslice-ring | 841 | 0 | 2 | 262 | 0.0078 | 0.0076 | 0.270 | 13.108 |
| first | 4 | bitslice-ring-int | 877 | 128 | 6 | 142 | 0.0081 | 0.0047 | 0.147 | 7.105 |
| vickrey | 4 | bitslice-ring-int | 1357 | 128 | 6 | 271 | 0.0120 | 0.0081 | 0.279 | 13.559 |
| first | 4 | tournament-ring | 183 | 102 | 5 | 22 | 0.0026 | 0.0013 | 0.023 | 1.101 |
| vickrey | 4 | tournament-ring | 369 | 204 | 8 | 32 | 0.0051 | 0.0017 | 0.034 | 1.602 |
| first | 4 | bitslice-bin | 361 | 0 | 0 | 137 | 0.0002 | 0.0043 | 0.141 | 6.854 |
| vickrey | 4 | bitslice-bin | 841 | 0 | 0 | 266 | 0.0004 | 0.0080 | 0.274 | 13.308 |
| first | 4 | tournament-bin | 300 | 0 | 0 | 22 | 0.0001 | 0.0012 | 0.023 | 1.101 |
| vickrey | 4 | tournament-bin | 792 | 0 | 0 | 38 | 0.0002 | 0.0016 | 0.040 | 1.902 |
| first | 8 | bitslice-ring | 761 | 0 | 2 | 166 | 0.0082 | 0.0051 | 0.171 | 8.306 |
| vickrey | 8 | bitslice-ring | 1753 | 0 | 2 | 327 | 0.0161 | 0.0097 | 0.337 | 16.361 |
| first | 8 | bitslice-ring-int | 1793 | 256 | 10 | 175 | 0.0165 | 0.0053 | 0.180 | 8.757 |
| vickrey | 8 | bitslice-ring-int | 2785 | 256 | 10 | 336 | 0.0245 | 0.0098 | 0.346 | 16.812 |
| first | 8 | tournament-ring | 427 | 238 | 9 | 31 | 0.0056 | 0.0017 | 0.033 | 1.552 |
| vickrey | 8 | tournament-ring | 861 | 476 | 16 | 42 | 0.0112 | 0.0021 | 0.044 | 2.103 |
| first | 8 | bitslice-bin | 761 | 0 | 0 | 170 | 0.0003 | 0.0049 | 0.175 | 8.505 |
| vickrey | 8 | bitslice-bin | 1753 | 0 | 0 | 331 | 0.0005 | 0.0094 | 0.340 | 16.559 |
| first | 8 | tournament-bin | 707 | 0 | 0 | 30 | 0.0002 | 0.0015 | 0.032 | 1.502 |
| vickrey | 8 | tournament-bin | 1855 | 0 | 0 | 54 | 0.0003 | 0.0022 | 0.056 | 2.702 |
| first | 16 | bitslice-ring | 1569 | 0 | 2 | 199 | 0.0167 | 0.0065 | 0.206 | 9.958 |
| vickrey | 16 | bitslice-ring | 3585 | 0 | 2 | 392 | 0.0328 | 0.0112 | 0.403 | 19.614 |
| first | 16 | bitslice-ring-int | 3633 | 512 | 18 | 208 | 0.0334 | 0.0068 | 0.215 | 10.409 |
| vickrey | 16 | bitslice-ring-int | 5649 | 512 | 18 | 401 | 0.0496 | 0.0114 | 0.413 | 20.065 |
| first | 16 | tournament-ring | 915 | 510 | 17 | 40 | 0.0117 | 0.0019 | 0.042 | 2.003 |
| vickrey | 16 | tournament-ring | 1845 | 1020 | 32 | 52 | 0.0233 | 0.0024 | 0.055 | 2.604 |
| first | 16 | bitslice-bin | 1569 | 0 | 0 | 203 | 0.0004 | 0.0063 | 0.209 | 10.156 |
| vickrey | 16 | bitslice-bin | 3585 | 0 | 0 | 396 | 0.0007 | 0.0108 | 0.407 | 19.811 |
| first | 16 | tournament-bin | 1530 | 0 | 0 | 38 | 0.0003 | 0.0018 | 0.040 | 1.902 |
| vickrey | 16 | tournament-bin | 3990 | 0 | 0 | 70 | 0.0006 | 0.0028 | 0.073 | 3.503 |
| first | 32 | bitslice-ring | 3201 | 0 | 2 | 232 | 0.0338 | 0.0072 | 0.239 | 11.610 |
| vickrey | 32 | bitslice-ring | 7265 | 0 | 2 | 457 | 0.0663 | 0.0128 | 0.470 | 22.868 |
| first | 32 | bitslice-ring-int | 7329 | 1024 | 34 | 241 | 0.0674 | 0.0076 | 0.249 | 12.063 |
| vickrey | 32 | bitslice-ring-int | 11393 | 1024 | 34 | 466 | 0.0999 | 0.0136 | 0.480 | 23.322 |
| first | 32 | tournament-ring | 1891 | 1054 | 33 | 49 | 0.0244 | 0.0023 | 0.051 | 2.454 |
| vickrey | 32 | tournament-ring | 3813 | 2108 | 64 | 62 | 0.0482 | 0.0030 | 0.065 | 3.107 |
| first | 32 | bitslice-bin | 3201 | 0 | 0 | 236 | 0.0007 | 0.0080 | 0.244 | 11.808 |
| vickrey | 32 | bitslice-bin | 7265 | 0 | 0 | 461 | 0.0012 | 0.0126 | 0.474 | 23.063 |
| first | 32 | tournament-bin | 3193 | 0 | 0 | 46 | 0.0006 | 0.0020 | 0.048 | 2.302 |
| vickrey | 32 | tournament-bin | 8277 | 0 | 0 | 86 | 0.0012 | 0.0031 | 0.089 | 4.303 |
| first | 64 | bitslice-ring | 6497 | 0 | 2 | 265 | 0.0684 | 0.0085 | 0.274 | 13.264 |
| vickrey | 64 | bitslice-ring | 14657 | 0 | 2 | 522 | 0.1337 | 0.0152 | 0.538 | 26.126 |
| first | 64 | bitslice-ring-int | 14753 | 2048 | 66 | 274 | 0.1354 | 0.0085 | 0.284 | 13.719 |
| vickrey | 64 | bitslice-ring-int | 22913 | 2048 | 66 | 531 | 0.2007 | 0.0147 | 0.547 | 26.581 |
| first | 64 | tournament-ring | 3843 | 2142 | 65 | 58 | 0.0492 | 0.0029 | 0.061 | 2.907 |
| vickrey | 64 | tournament-ring | 7749 | 4284 | 128 | 72 | 0.0978 | 0.0037 | 0.077 | 3.612 |
| first | 64 | bitslice-bin | 6497 | 0 | 0 | 269 | 0.0012 | 0.0078 | 0.277 | 13.458 |
| vickrey | 64 | bitslice-bin | 14657 | 0 | 0 | 526 | 0.0023 | 0.0151 | 0.541 | 26.315 |
| first | 64 | tournament-bin | 6552 | 0 | 0 | 54 | 0.0011 | 0.0023 | 0.056 | 2.702 |
| vickrey | 64 | tournament-bin | 16884 | 0 | 0 | 102 | 0.0024 | 0.0042 | 0.106 | 5.104 |
| first | 128 | bitslice-ring | 13153 | 0 | 2 | 298 | 0.1380 | 0.0105 | 0.310 | 14.922 |
| vickrey | 128 | bitslice-ring | 29505 | 0 | 2 | 587 | 0.2688 | 0.0194 | 0.609 | 29.391 |
| first | 128 | bitslice-ring-int | 29665 | 4096 | 130 | 307 | 0.2722 | 0.0107 | 0.320 | 15.382 |
| vickrey | 128 | bitslice-ring-int | 46017 | 4096 | 130 | 596 | 0.4030 | 0.0196 | 0.619 | 29.852 |
| first | 128 | tournament-ring | 7747 | 4318 | 129 | 67 | 0.0988 | 0.0038 | 0.072 | 3.362 |
| vickrey | 128 | tournament-ring | 15621 | 8636 | 256 | 82 | 0.1972 | 0.0051 | 0.089 | 4.121 |
| first | 128 | bitslice-bin | 13153 | 0 | 0 | 302 | 0.0023 | 0.0098 | 0.312 | 15.110 |
| vickrey | 128 | bitslice-bin | 29505 | 0 | 0 | 591 | 0.0044 | 0.0182 | 0.609 | 29.569 |
| first | 128 | tournament-bin | 13335 | 0 | 0 | 62 | 0.0022 | 0.0029 | 0.065 | 3.103 |
| vickrey | 128 | tournament-bin | 34163 | 0 | 0 | 118 | 0.0049 | 0.0043 | 0.122 | 5.905 |
| first | 256 | bitslice-ring | 26593 | 0 | 2 | 331 | 0.2783 | 0.0134 | 0.347 | 16.586 |
| vickrey | 256 | bitslice-ring | 59329 | 0 | 2 | 652 | 0.5402 | 0.0236 | 0.680 | 32.667 |
| first | 256 | bitslice-ring-int | 59617 | 8192 | 258 | 340 | 0.5466 | 0.0139 | 0.358 | 17.058 |
| vickrey | 256 | bitslice-ring-int | 92353 | 8192 | 258 | 661 | 0.8085 | 0.0215 | 0.689 | 33.136 |
| first | 256 | tournament-ring | 15555 | 8670 | 257 | 76 | 0.1982 | 0.0050 | 0.083 | 3.821 |
| vickrey | 256 | tournament-ring | 31365 | 17340 | 512 | 94 | 0.3963 | 0.0064 | 0.104 | 4.738 |
| first | 256 | bitslice-bin | 26593 | 0 | 0 | 335 | 0.0045 | 0.0098 | 0.345 | 16.760 |
| vickrey | 256 | bitslice-bin | 59329 | 0 | 0 | 656 | 0.0086 | 0.0190 | 0.675 | 32.820 |
| first | 256 | tournament-bin | 27030 | 0 | 0 | 70 | 0.0045 | 0.0032 | 0.073 | 3.504 |
| vickrey | 256 | tournament-bin | 68850 | 0 | 0 | 134 | 0.0097 | 0.0055 | 0.140 | 6.706 |

## Semi-honest vs malicious (Vickrey, k = 32)

| variant | n | security | rounds | MB/server | local s |
|---|---|---|---|---|---|
| bitslice-ring | 4 | semi-honest | 262 | 0.0078 | 0.0079 |
| bitslice-ring | 4 | malicious | 273 | 0.0477 | 0.0098 |
| tournament-ring | 4 | semi-honest | 32 | 0.0051 | 0.0018 |
| tournament-ring | 4 | malicious | 58 | 0.0318 | 0.0036 |
| bitslice-bin | 4 | semi-honest | 266 | 0.0004 | 0.0082 |
| bitslice-bin | 4 | malicious | 274 | 0.1117 | 0.0101 |
| tournament-bin | 4 | semi-honest | 38 | 0.0002 | 0.0019 |
| tournament-bin | 4 | malicious | 46 | 0.1154 | 0.0041 |
| bitslice-ring | 16 | semi-honest | 392 | 0.0328 | 0.0114 |
| bitslice-ring | 16 | malicious | 403 | 0.2017 | 0.0151 |
| tournament-ring | 16 | semi-honest | 52 | 0.0233 | 0.0027 |
| tournament-ring | 16 | malicious | 82 | 0.1551 | 0.0079 |
| bitslice-bin | 16 | semi-honest | 396 | 0.0007 | 0.0117 |
| bitslice-bin | 16 | malicious | 404 | 0.1140 | 0.0138 |
| tournament-bin | 16 | semi-honest | 70 | 0.0006 | 0.0030 |
| tournament-bin | 16 | malicious | 78 | 0.1240 | 0.0049 |
| bitslice-ring | 64 | semi-honest | 522 | 0.1337 | 0.0166 |
| bitslice-ring | 64 | malicious | 538 | 0.8231 | 0.0269 |
| tournament-ring | 64 | semi-honest | 72 | 0.0978 | 0.0039 |
| tournament-ring | 64 | malicious | 106 | 0.6477 | 0.0221 |
| bitslice-bin | 64 | semi-honest | 526 | 0.0023 | 0.0151 |
| bitslice-bin | 64 | malicious | 534 | 0.1170 | 0.0187 |
| tournament-bin | 64 | semi-honest | 102 | 0.0024 | 0.0039 |
| tournament-bin | 64 | malicious | 110 | 0.1329 | 0.0059 |
