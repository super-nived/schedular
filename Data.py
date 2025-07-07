ROUTING_DATA = [
{
  "CHW/DX/Cond.S": {
    "header": [
      { "field": "RecipeID", "value": "R2" },
      { "field": "Dimension", "value": "3/8\"" },
      { "field": "Pitch", "value": "0.86\"" }
    ],
    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [
          { "field": "Mat", "op": "==", "value": "Cu" }
        ],
        "machines": [
          { "id": "FP001", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 150"},
          { "id": "FP002", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 150"},
        ]
      },
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP001", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
          { "id": "FP002", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
          { "id": "FP006", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
          { "id": "FP008", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
        ]
      }
    ],
    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          {
            "id": "SM001",
            "desc": "Shearing M/C 7T",
            "preferred": True,
            "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"
          },
          {
            "id": "SM002",
            "desc": "Durma shearing M/C",
            "preferred": True,
            "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"
          }
        ]
      }
    ],
    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          {
            "id": "CNCMC002",
            "desc": "CNC Punching Machine-2",
            "preferred": True,
            "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"

          },
          {
            "id": "CNCMC003",
            "desc": "CNC Punching Machine-3",
            "preferred": False,
            "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"
          }
        ]
      }
    ],
    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          {
            "id": "BB001",
            "desc": "Bending press brake 80T",
            "preferred": True,
            "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"
          },
          {
            "id": "YSDCNC001",
            "desc": "YSD CNC Press brake",
            "preferred": False,
            "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"
          }
        ]
      }
    ],
    "Hairpin bend": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          {
            "id": "VBHB001",
            "desc": "Hairpin bender-1",
            "preferred": True,
            "time-formula": "((((FL + 100)/1000) * (FH/25.4/2) * Row * Qty) / 4) * 50 / 60"

          },
          {
            "id": "VBHB003",
            "desc": "Hairpin bender-3",
            "preferred": True,
            "time-formula": "((((FL + 100)/1000) * (FH/25.4/2) * Row * Qty) / 4) * 50 / 60"

          }
        ]
      }
    ],
    "Cut to length": [
      {
        "sequence": 6,
        "conditions": [
          {
            "field": "FL",
            "op": ">",
            "value": 3660
          }
        ],
        "machines": [
          {
            "id": "T001",
            "desc": "Tridan cut to length m/c.",
            "preferred": True,
            "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60"

          }
        ]
      }
    ],
    "Trimming & Flaring": [
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          {
            "id": "TF001",
            "desc": "Trimming Flaring - Manual",
            "preferred": True,
            "time-formula": "(FH/25.4) * Row * Qty * 0.33"

          }
        ]
      }
    ],
    "Return Bend Loading": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          {
            "id": "RBL001",
            "desc": "Return Bend Loading - Manual",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Return Bend Brazing": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          {
            "id": "RBB001",
            "desc": "Return Bend Brazing - Manual",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Header Cutting": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          {
            "id": "PC001",
            "desc": "Pipe Cutting",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Header Bending": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          {
            "id": "TBMC001",
            "desc": "YLM Tube Bending M/C",
            "preferred": False,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Header Drilling": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          {
            "id": "HBDMC001",
            "desc": "SKB Header brazing / Drilling M/C",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          },
          {
            "id": "CNCDMC001",
            "desc": "SKB 4 Axis CNC drilling machine",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Header End Closing": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          {
            "id": "TESMC001",
            "desc": "Tube end closing Machine",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          },
          {
            "id": "TESMC002",
            "desc": "Tube end closing Machine",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Header Branching": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          {
            "id": "TD001",
            "desc": "T-Forming M/C - HFT-2000",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Header Hole Piercing": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          {
            "id": "H001",
            "desc": "Header hole piercing & Extrusion",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Feeder Cut": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          {
            "id": "T002",
            "desc": "JDM cut to length m/c",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Header Sub Assembly": [
      {
        "sequence": 17,
        "conditions": [],
        "machines": [
          {
            "id": "Manual001",
            "desc": "Brazing - Manual",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Header to Coil": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          {
            "id": "Manual002",
            "desc": "Brazing - Manual",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Leak Testing": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          {
            "id": "Tank1",
            "desc": "Leak Testing tank - 1",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          },
          {
            "id": "Tank2",
            "desc": "Leak Testing tank - 2",
            "preferred": False,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Coil Degreasing": [
      {
        "sequence": 20,
        "conditions": [],
        "machines": [
          {
            "id": "DegreasingCS1",
            "desc": "Karcher Cleaning Machine 2",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          },
          {
            "id": "DegreasingCS2",
            "desc": "Karcher Cleaning Machine 3",
            "preferred": True,
            "time-formula": "(FH/25.4/2) * Row * Qty * 0.2"

          }
        ]
      }
    ],
    "Coating": [
      {
        "sequence": 21,
        "conditions": [],
        "machines": [
          {
            "id": "Booth1",
            "desc": "Coating booth - 1",
            "preferred": True,
            "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18"

          },
          {
            "id": "Booth2",
            "desc": "Coating booth - 2",
            "preferred": True,
            "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18"

          },
          {
            "id": "Booth3",
            "desc": "Coating booth - 3",
            "preferred": True,
            "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18"

          }
        ]
      }
    ]
  }
},
{
  "CHW/DX/Cond.S": {
    "header": [
      { "field": "RecipeID", "value": "R1" },
      { "field": "Dimension", "value": "3/8\"" },
      { "field": "Pitch",     "value": "0.75\"" }
    ],

    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP001", "desc": "Fin Press - 1",                  "preferred": True }
        ]
      }
    ],

    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          { "id": "SM001", "desc": "Shearing M/C 7T",               "preferred": True },
          { "id": "SM002", "desc": "Durma shearing M/C",            "preferred": True }
        ]
      }
    ],

    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          { "id": "CNCMC002", "desc": "CNC Punching Machine-2",      "preferred": True },
          { "id": "CNCMC003", "desc": "CNC Punching Machine-3",      "preferred": False }
        ]
      }
    ],

    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          { "id": "BB001",      "desc": "Bending press brake 80T",  "preferred": True },
          { "id": "YSDCNC001", "desc": "YSD CNC Press brake",      "preferred": False }
        ]
      }
    ],

    "Hairpin bend": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          { "id": "VBHB003", "desc": "Hairpin bender-3",            "preferred": True }
        ]
      }
    ],

    "Cut to length": [
      {
        "sequence": 6,
        "conditions": [
          { "field": "FL", "op": ">", "value": 3600 }
        ],
        "machines": [
          { "id": "T001", "desc": "Tridan cut to length m/c.",     "preferred": True }
        ]
      }
    ],

    "Expansion": [
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          { "id": "FB003", "desc": "Flexpander with     balancer -3",  "preferred": True },
          { "id": "FB005", "desc": "Flexpander with     balancer -5",  "preferred": True }
        ]
      }
    ],

    "Trimming & Flaring": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          { "id": "TF001", "desc": "Trimming Flaring - Manual",     "preferred": True }
        ]
      }
    ],

    "Return Bend Loading": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          { "id": "RBL001", "desc": "Return Bend Loading - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Brazing": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          { "id": "RBB001", "desc": "Return Bend Brazing - Manual", "preferred": True }
        ]
      }
    ],

    "Header Cutting": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          { "id": "PC001", "desc": "Pipe Cutting",               "preferred": True }
        ]
      }
    ],

    "Header Bending": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          { "id": "TBMC001", "desc": "YLM Tube Bending M/C",     "preferred": False }
        ]
      }
    ],

    "Header Drilling": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          { "id": "HBDMC001", "desc": "SKB Header brazing / Drilling M/C", "preferred": True },
          { "id": "CNCDMC001","desc": "SKB 4 Axis CNC drilling machine","preferred": True }
        ]
      }
    ],

    "Header End Closing": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          { "id": "TESMC001","desc": "Tube end closing Machine",       "preferred": True },
          { "id": "TESMC002","desc": "Tube end closing Machine",       "preferred": True }
        ]
      }
    ],

    "Header Branching": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          { "id": "TD001","desc": "T-Forming M/C - HFT-2000",         "preferred": True }
        ]
      }
    ],

    "Header Hole Piercing": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          { "id": "H001","desc": "Header hole piercing & Extrusion","preferred": False }
        ]
      }
    ],

    "Feeder Cut": [
      {
        "sequence": 17,
        "conditions": [],
        "machines": [
          { "id": "T002","desc": "JDM cut to length m/c",             "preferred": True }
        ]
      }
    ],

    "Header Sub Assembly": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          { "id": "Manual001","desc": "Brazing - Manual",             "preferred": True }
        ]
      }
    ],

    "Header to Coil": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          { "id": "Manual002","desc": "Brazing - Manual",             "preferred": True }
        ]
      }
    ],

    "Leak Testing": [
      {
        "sequence": 20,
        "conditions": [],
        "machines": [
          { "id": "Tank1","desc": "Leak Testing tank - 2",          "preferred": True },
          { "id": "Tank2","desc": "Leak Testing tank - 2",          "preferred": False }
        ]
      }
    ],

    "Coil Degreasing": [
      {
        "sequence": 21,
        "conditions": [],
        "machines": [
          { "id": "DegreasingCS1","desc": "Karcher Cleaning Machine 2","preferred": True },
          { "id": "DegreasingCS2","desc": "Karcher Cleaning Machine 3","preferred": True }
        ]
      }
    ],

    "Coating": [
      {
        "sequence": 22,
        "conditions": [],
        "machines": [
          { "id": "Booth1","desc": "Coating booth - 1",             "preferred": True },
          { "id": "Booth2","desc": "Coating booth - 2",             "preferred": True },
          { "id": "Booth3","desc": "Coating booth - 3",             "preferred": True }
        ]
      }
    ]
  }
},
{
  "CHW/DX/Cond.S": {
    "header": [
      { "field": "RecipeID", "value": "R1" },
      { "field": "Dimension", "value": "1/2\"" },
      { "field": "Pitch",     "value": "1/2" }
    ],

    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [
          { "field": "Mat", "op": "==", "value": "Cu" }
        ],
        "machines": [
          { "id": "FP001", "desc": "Fin Press - 1", "preferred": True },
          { "id": "FP002", "desc": "Fin Press - 2", "preferred": True }
        ]
      },
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP007", "desc": "Fin Press - 7 (1/2\")", "preferred": True },
          { "id": "FP001", "desc": "Fin Press - 1", "preferred": True },
          { "id": "FP002", "desc": "Fin Press - 2", "preferred": True }
        ]
      }
    ],

    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          { "id": "SM001", "desc": "Shearing M/C 7T", "preferred": True },
          { "id": "SM002", "desc": "Durma shearing M/C", "preferred": True }
        ]
      }
    ],

    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          { "id": "CNCMC002", "desc": "CNC Punching Machine-2", "preferred": False },
          { "id": "CNCMC003", "desc": "CNC Punching Machine-3", "preferred": True }
        ]
      }
    ],

    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          { "id": "BB001",      "desc": "Bending press brake 80T", "preferred": True },
          { "id": "YSDCNC001", "desc": "YSD CNC Press brake",     "preferred": True }
        ]
      }
    ],

    "Hairpin bend": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          { "id": "VBHB002", "desc": "Hairpin bender-2", "preferred": True }
        ]
      }
    ],

    "Cut to length": [
      {
        "sequence": 6,
        "conditions": [
          { "field": "FL", "op": ">", "value": 2800 }
        ],
        "machines": [
          { "id": "T001", "desc": "Tridan cut to length m/c.", "preferred": True }
        ]
      },
      {
        "sequence": 6,
        "conditions": [],
        "machines": [
          { "id": "T002", "desc": "BP cut to length m/c.", "preferred": True }
        ]
      }
    ],

    "Expansion": [
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          { "id": "FB004", "desc": "Flexpander with     balancer -4", "preferred": True }
        ]
      }
    ],

    "Trimming & Flaring": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          { "id": "TF001", "desc": "Trimming Flaring - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Loading": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          { "id": "RBL001", "desc": "Return Bend Loading - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Brazing": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          { "id": "RBB001", "desc": "Return Bend Brazing - Manual", "preferred": True }
        ]
      }
    ],

    "Header Cutting": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          { "id": "PC001", "desc": "Pipe Cutting", "preferred": True }
        ]
      }
    ],

    "Header Drilling": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          { "id": "HBDMC001", "desc": "SKB Header brazing / Drilling M/C", "preferred": True },
          { "id": "CNCDMC001","desc": "SKB 4 Axis CNC drilling machine","preferred": True }
        ]
      }
    ],

    "Header End Closing": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          { "id": "TESMC001","desc": "Tube end closing Machine",       "preferred": True },
          { "id": "TESMC002","desc": "Tube end closing Machine",       "preferred": True }
        ]
      }
    ],

    "Header Branching": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          { "id": "TD001","desc": "T-Forming M/C - HFT-2000",         "preferred": True }
        ]
      }
    ],

    "Header Hole Piercing": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          { "id": "H001","desc": "Header hole piercing & Extrusion","preferred": True }
        ]
      }
    ],

    "Feeder Cut": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          { "id": "T002","desc": "JDM cut to length m/c","preferred": True }
        ]
      }
    ],

    "Header Sub Assembly": [
      {
        "sequence": 17,
        "conditions": [],
        "machines": [
          { "id": "Manual001","desc": "Brazing - Manual","preferred": True }
        ]
      }
    ],

    "Header to Coil": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          { "id": "Manual002","desc": "Brazing - Manual","preferred": True }
        ]
      }
    ],

    "Leak Testing": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          { "id": "Tank2","desc": "Leak Testing tank - 2","preferred": True }
        ]
      }
    ],

    "Coil Degreasing": [
      {
        "sequence": 20,
        "conditions": [],
        "machines": [
          { "id": "DegreasingCS1","desc": "Karcher Cleaning Machine 2","preferred": True },
          { "id": "DegreasingCS2","desc": "Karcher Cleaning Machine 3","preferred": True }
        ]
      }
    ],

    "Coating": [
      {
        "sequence": 21,
        "conditions": [],
        "machines": [
          { "id": "Booth1","desc": "Coating booth - 1","preferred": True },
          { "id": "Booth2","desc": "Coating booth - 2","preferred": True },
          { "id": "Booth3","desc": "Coating booth - 3","preferred": True }
        ]
      }
    ]
  }
},
{
  "CHW/DX": {
    "header": [
      { "field": "RecipeID", "value": "R1" },
      { "field": "Dimension", "value": "5/8\"" },
      { "field": "Pitch",     "value": "1.5\"" }
    ],

    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP002", "desc": "Fin Press - 2",                       "preferred": True }
        ]
      }
    ],

    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          { "id": "SM001", "desc": "Shearing M/C 7T",                    "preferred": True },
          { "id": "SM002", "desc": "Durma shearing M/C",                 "preferred": True }
        ]
      }
    ],

    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          { "id": "CNCMC002", "desc": "CNC Punching Machine-2",           "preferred": False },
          { "id": "CNCMC003", "desc": "CNC Punching Machine-3",           "preferred": True }
        ]
      }
    ],

    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          { "id": "BB001",      "desc": "Bending press brake 80T",       "preferred": True },
          { "id": "YSDCNC001", "desc": "YSD CNC Press brake",            "preferred": True }
        ]
      }
    ],

    "Cut to length": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          { "id": "T001", "desc": "Tridan cut to length m/c.",         "preferred": True },
          { "id": "T002", "desc": "BP cut to length m/c.",             "preferred": True }
        ]
      }
    ],

    "Expansion": [
      {
        "sequence": 6,
        "conditions": [],
        "machines": [
          { "id": "HB001", "desc": "Hexpander with balancer",           "preferred": True }
        ]
      }
    ],

    "Trimming & Flaring": [
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          { "id": "TF001", "desc": "Trimming Flaring - Manual",         "preferred": True }
        ]
      }
    ],

    "Return Bend Loading": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          { "id": "RBL001", "desc": "Return Bend Loading - Manual",      "preferred": True }
        ]
      }
    ],

    "Return Bend Brazing": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          { "id": "RBB001", "desc": "Return Bend Brazing - Manual",      "preferred": True }
        ]
      }
    ],

    "Header Cutting": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          { "id": "PC001", "desc": "Pipe Cutting",                       "preferred": True }
        ]
      }
    ],

    "Header Drilling": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          { "id": "HBDMC001", "desc": "SKB Header brazing / Drilling M/C", "preferred": True },
          { "id": "CNCDMC001","desc": "SKB 4 Axis CNC drilling machine",   "preferred": True }
        ]
      }
    ],

    "Header End Closing": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          { "id": "TESMC001","desc": "Tube end closing Machine",          "preferred": True },
          { "id": "TESMC002","desc": "Tube end closing Machine",          "preferred": True }
        ]
      }
    ],

    "Header Branching": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          { "id": "TD001","desc": "T-Forming M/C - HFT-2000",             "preferred": True }
        ]
      }
    ],

    "Header Hole Piercing": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          { "id": "H001","desc": "Header hole piercing & Extrusion",    "preferred": True }
        ]
      }
    ],

    "Feeder Cut": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          { "id": "T002","desc": "JDM cut to length m/c",               "preferred": True }
        ]
      }
    ],

    "Header Sub Assembly": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          { "id": "Manual001","desc": "Brazing - Manual",                 "preferred": True }
        ]
      }
    ],

    "Header to Coil": [
      {
        "sequence": 17,
        "conditions": [],
        "machines": [
          { "id": "Manual002","desc": "Brazing - Manual",                 "preferred": True }
        ]
      }
    ],

    "Leak Testing": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          { "id": "Tank3","desc": "Leak Testing tank - 3",              "preferred": True }
        ]
      }
    ],

    "Coil Degreasing": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          { "id": "DegreasingCS1","desc": "Karcher Cleaning Machine 2",  "preferred": True },
          { "id": "DegreasingCS2","desc": "Karcher Cleaning Machine 3",  "preferred": True }
        ]
      }
    ],

    "Coating": [
      {
        "sequence": 20,
        "conditions": [],
        "machines": [
          { "id": "Booth1","desc": "Coating booth - 1",                  "preferred": True },
          { "id": "Booth2","desc": "Coating booth - 2",                  "preferred": True },
          { "id": "Booth3","desc": "Coating booth - 3",                  "preferred": True }
        ]
      }
    ]
  }
}
,
{
  "CHW": {
    "header": [
      { "field": "RecipeID",   "value": "R1" },
      { "field": "Dimension",  "value": "5/8\"" },
      { "field": "Pitch",      "value": "60x30" }
    ],
    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP003", "desc": "Fin Press - 3", "preferred": True }
        ]
      }
    ],
    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          { "id": "SM001", "desc": "Shearing M/C 7T", "preferred": True },
          { "id": "SM002", "desc": "Durma shearing M/C", "preferred": True }
        ]
      }
    ],
    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          { "id": "CNCMC002", "desc": "CNC Punching Machine-2", "preferred": False },
          { "id": "CNCMC003", "desc": "CNC Punching Machine-3",   "preferred": True }
        ]
      }
    ],
    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          { "id": "BB001",      "desc": "Bending press brake 80T", "preferred": True },
          { "id": "YSDCNC001", "desc": "YSD CNC Press brake",     "preferred": True }
        ]
      }
    ],
    "Cut to length": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          { "id": "T001", "desc": "Tridan cut to length m/c.", "preferred": True },
          { "id": "T002", "desc": "BP cut to length m/c.",     "preferred": True }
        ]
      }
    ],
    "Expansion": [
      {
        "sequence": 6,
        "conditions": [],
        "machines": [
          { "id": "HB001", "desc": "Hexpander with balancer", "preferred": True }
        ]
      }
    ],
    "Trimming & Flaring": [
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          { "id": "TF001", "desc": "Trimming Flaring - Manual", "preferred": True }
        ]
      }
    ],
    "Return Bend Loading": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          { "id": "RBL001", "desc": "Return Bend Loading - Manual", "preferred": True }
        ]
      }
    ],
    "Header Cutting": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          { "id": "PC001", "desc": "Pipe Cutting", "preferred": True }
        ]
      }
    ],
    "Header Drilling": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          { "id": "HBDMC001", "desc": "SKB Header brazing / Drilling M/C", "preferred": True },
          { "id": "CNCDMC001","desc": "SKB 4 Axis CNC drilling machine",    "preferred": True }
        ]
      }
    ],
    "Header End Closing": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          { "id": "TESMC001","desc": "Tube end closing Machine",          "preferred": True },
          { "id": "TESMC002","desc": "Tube end closing Machine",          "preferred": True }
        ]
      }
    ],
    "Header Branching": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          { "id": "TD001","desc": "T-Forming M/C - HFT-2000",                "preferred": True }
        ]
      }
    ],
    "Header Hole Piercing": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          { "id": "H001","desc": "Header hole piercing & Extrusion",          "preferred": True }
        ]
      }
    ],
    "Feeder Cut": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          { "id": "T002","desc": "JDM cut to length m/c",                   "preferred": True }
        ]
      }
    ],
    "Header Sub Assembly": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          { "id": "Manual001","desc": "Brazing - Manual",                  "preferred": True }
        ]
      }
    ],
    "Header to Coil": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          { "id": "Manual002","desc": "Brazing - Manual",                  "preferred": True }
        ]
      }
    ],
    "Leak Testing": [
      {
        "sequence": 17,
        "conditions": [],
        "machines": [
          { "id": "Tank3","desc": "Leak Testing tank - 3",                "preferred": True }
        ]
      }
    ],
    "Coil Degreasing": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          { "id": "DegreasingCS1","desc": "Karcher Cleaning Machine 2",      "preferred": True },
          { "id": "DegreasingCS2","desc": "Karcher Cleaning Machine 3",      "preferred": True }
        ]
      }
    ],
    "Coating": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          { "id": "Booth1","desc": "Coating booth - 1",                      "preferred": True },
          { "id": "Booth2","desc": "Coating booth - 2",                      "preferred": True },
          { "id": "Booth3","desc": "Coating booth - 3",                      "preferred": True }
        ]
      }
    ]
  }
},
{
  "CHW/DX": {
    "header": [
      { "field": "RecipeID", "value": "R1" },
      { "field": "Dimension", "value": "5/8\"" },
      { "field": "Pitch",     "value": "P40" }
    ],

    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP003", "desc": "Fin Press - 3", "preferred": True }
        ]
      }
    ],

    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          { "id": "SM001", "desc": "Shearing M/C 7T", "preferred": True },
          { "id": "SM002", "desc": "Durma shearing M/C", "preferred": True }
        ]
      }
    ],

    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          { "id": "CNCMC002", "desc": "CNC Punching Machine-2", "preferred": False },
          { "id": "CNCMC003", "desc": "CNC Punching Machine-3", "preferred": True }
        ]
      }
    ],

    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          { "id": "BB001",      "desc": "Bending press brake 80T", "preferred": True },
          { "id": "YSDCNC001", "desc": "YSD CNC Press brake",     "preferred": True }
        ]
      }
    ],

    "Cut to length": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          { "id": "T001", "desc": "Tridan cut to length m/c.", "preferred": True },
          { "id": "T002", "desc": "BP cut to length m/c.",     "preferred": True }
        ]
      }
    ],

    "Expansion": [
      {
        "sequence": 6,
        "conditions": [],
        "machines": [
          { "id": "HB001", "desc": "Hexpander with balancer", "preferred": True }
        ]
      }
    ],

    "Trimming & Flaring": [
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          { "id": "TF001", "desc": "Trimming Flaring - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Loading": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          { "id": "RBL001", "desc": "Return Bend Loading - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Brazing": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          { "id": "RBB001", "desc": "Return Bend Brazing - Manual", "preferred": True }
        ]
      }
    ],

    "Header Cutting": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          { "id": "PC001", "desc": "Pipe Cutting", "preferred": True }
        ]
      }
    ],

    "Header Drilling": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          { "id": "HBDMC001", "desc": "SKB Header brazing / Drilling M/C", "preferred": True },
          { "id": "CNCDMC001","desc": "SKB 4 Axis CNC drilling machine",  "preferred": True }
        ]
      }
    ],

    "Header End Closing": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          { "id": "TESMC001","desc": "Tube end closing Machine",            "preferred": True },
          { "id": "TESMC002","desc": "Tube end closing Machine",            "preferred": True }
        ]
      }
    ],

    "Header Branching": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          { "id": "TD001","desc": "T-Forming M/C - HFT-2000",                "preferred": True }
        ]
      }
    ],

    "Header Hole Piercing": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          { "id": "H001","desc": "Header hole piercing & Extrusion",          "preferred": True }
        ]
      }
    ],

    "Feeder Cut": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          { "id": "T002","desc": "JDM cut to length m/c",                   "preferred": True }
        ]
      }
    ],

    "Header Sub Assembly": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          { "id": "Manual001","desc": "Brazing - Manual",                  "preferred": True }
        ]
      }
    ],

    "Header to Coil": [
      {
        "sequence": 17,
        "conditions": [],
        "machines": [
          { "id": "Manual002","desc": "Brazing - Manual",                  "preferred": True }
        ]
      }
    ],

    "Leak Testing": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          { "id": "Tank3","desc": "Leak Testing tank - 3",                "preferred": True }
        ]
      }
    ],

    "Coil Degreasing": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          { "id": "DegreasingCS1","desc": "Karcher Cleaning Machine 2",      "preferred": True },
          { "id": "DegreasingCS2","desc": "Karcher Cleaning Machine 3",      "preferred": True }
        ]
      }
    ],

    "Coating": [
      {
        "sequence": 20,
        "conditions": [],
        "machines": [
          { "id": "Booth1","desc": "Coating booth - 1",                      "preferred": True },
          { "id": "Booth2","desc": "Coating booth - 2",                      "preferred": True },
          { "id": "Booth3","desc": "Coating booth - 3",                      "preferred": True }
        ]
      }
    ]
  }
},
{
  "Cond.B": {
    "header": [
      { "field": "RecipeID", "value": "R1" },
      { "field": "Dimension", "value": "3/8\"" },
      { "field": "Pitch",     "value": "0.86\"" }
    ],

    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [
          { "field": "Mat",  "op": "==", "value": "Cu" }
        ],
        "machines": [
          { "id": "FP001", "desc": "Fin Press - 1",                  "preferred": True },
          { "id": "FP002", "desc": "Fin Press - 2",                  "preferred": True }
        ]
      },
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP006", "desc": "Fin Press - 6 (3/8\"X0.866\")",  "preferred": True },
          { "id": "FP008", "desc": "Fin Press - 8 (3/8\"X0.866\")",  "preferred": True },
          { "id": "FP001", "desc": "Fin Press - 1",                  "preferred": True },
          { "id": "FP002", "desc": "Fin Press - 2",                  "preferred": True }
        ]
      }
    ],

    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          { "id": "SM001", "desc": "Shearing M/C 7T",               "preferred": True },
          { "id": "SM002", "desc": "Durma shearing M/C",            "preferred": True }
        ]
      }
    ],

    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          { "id": "CNCMC002", "desc": "CNC Punching Machine-2",      "preferred": True },
          { "id": "CNCMC003", "desc": "CNC Punching Machine-3",      "preferred": False }
        ]
      }
    ],

    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          { "id": "BB001",      "desc": "Bending press brake 80T",  "preferred": True },
          { "id": "YSDCNC001", "desc": "YSD CNC Press brake",      "preferred": False }
        ]
      }
    ],

    "Hairpin bend": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          { "id": "VBHB001", "desc": "Hairpin bender-1",            "preferred": True },
          { "id": "VBHB003", "desc": "Hairpin bender-3",            "preferred": True }
        ]
      }
    ],

    "Cut to length": [
      {
        "sequence": 6,
        "conditions": [],
        "machines": [
          { "id": "T001", "desc": "Tridan cut to length m/c.",     "preferred": True }
        ]
      }
    ],

    "Expansion": [
      {
        "sequence": 7,
        "conditions": [
          { "field": "Qty",   "op": ">=", "value": 10 },
          { "field": "FL",    "op": "<",  "value": 1500 },
          { "field": "FH",    "op": "<",  "value": 1219.2 },
          { "field": "Row",   "op": "<=", "value": 2 },
          { "field": "L2-L1", "op": "<=", "value": 50 },
          { "field": "L2-L1", "op": ">", "value": 1 }
        ],
        "machines": [
          { "id": "VEMC001", "desc": "Vertical expander machine",  "preferred": True }
        ]
      },
      {
        "sequence": 7,
        "conditions": [
          { "field": "Qty",   "op": ">=", "value": 10 },
          { "field": "FL",    "op": "<",  "value": 2500 },
          { "field": "FH",    "op": "<",  "value": 1219.2 },
          { "field": "Row",   "op": "<=", "value": 3 },
          { "field": "L1",    "op": "==", "valueField": "L2" },
          { "field": "L2",    "op": "==", "valueField": "L3" }
        ],
        "machines": [
          { "id": "VEMC002", "desc": "Vertical expander machine",  "preferred": True }
        ]
      },
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          { "id": "FB003", "desc": "Flexpander with balancer -3",  "preferred": True },
          { "id": "FB005", "desc": "Flexpander with balancer -5",  "preferred": True }
        ]
      }
    ],

    "Coil Bending": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          { "id": "CBMC002", "desc": "Coil bending machine",      "preferred": True }
        ]
      }
    ],

    "Trimming & Flaring": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          { "id": "TF001", "desc": "Trimming & Flaring - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Loading": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          { "id": "RBL001", "desc": "Return Bend Loading - Manual","preferred": True }
        ]
      }
    ],

    "Return Bend Brazing": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          { "id": "RBB001", "desc": "Return Bend Brazing - Manual","preferred": True }
        ]
      }
    ],

    "Header Cutting": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          { "id": "PC001", "desc": "Pipe Cutting",               "preferred": True }
        ]
      }
    ],

    "Header Bending": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          { "id": "TBMC001", "desc": "YLM Tube Bending M/C",     "preferred": False }
        ]
      }
    ],

    "Header Drilling": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          { "id": "HBDMC001", "desc": "SKB Header brazing/Drilling M/C","preferred": True },
          { "id": "CNCDMC001","desc":"SKB 4 Axis CNC drilling machine","preferred": True }
        ]
      }
    ],

    "Header End Closing": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          { "id": "TESMC001","desc":"Tube end closing Machine","preferred": True },
          { "id": "TESMC002","desc":"Tube end closing Machine","preferred": True }
        ]
      }
    ],

    "Header Branching": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          { "id": "TD001","desc":"T-Forming M/C - HFT-2000","preferred": True }
        ]
      }
    ],

    "Header Hole Piercing": [
      {
        "sequence": 17,
        "conditions": [],
        "machines": [
          { "id": "H001","desc":"Header hole piercing & Extrusion","preferred": True },
          { "id": "T002","desc":"JDM cut to length m/c","preferred": True }
        ]
      }
    ],

    "Feeder Cut": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          { "id": "T002","desc":"JDM cut to length m/c","preferred": True }
        ]
      }
    ],

    "Header Sub Assembly": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          { "id": "Manual001","desc":"Brazing - Manual","preferred": True }
        ]
      }
    ],

    "Header to Coil": [
      {
        "sequence": 20,
        "conditions": [],
        "machines": [
          { "id": "Manual002","desc":"Brazing - Manual","preferred": True }
        ]
      }
    ],

    "Leak Testing": [
      {
        "sequence": 21,
        "conditions": [],
        "machines": [
          { "id": "Tank1","desc":"Leak Testing tank - 1","preferred": True },
          { "id": "Tank2","desc":"Leak Testing tank - 2","preferred": False }
        ]
      }
    ],

    "Coil Degreasing": [
      {
        "sequence": 22,
        "conditions": [],
        "machines": [
          { "id": "DegreasingCS1","desc":"Karcher Cleaning Machine 2","preferred": True },
          { "id": "DegreasingCS2","desc":"Karcher Cleaning Machine 3","preferred": True }
        ]
      }
    ],

    "Coating": [
      {
        "sequence": 23,
        "conditions": [],
        "machines": [
          { "id": "Booth1","desc":"Coating booth - 1","preferred": True },
          { "id": "Booth2","desc":"Coating booth - 2","preferred": True },
          { "id": "Booth3","desc":"Coating booth - 3","preferred": True }
        ]
      }
    ]
  }
},
{
  "Cond.B": {
    "header": [
      { "field": "RecipeID", "value": "R1" },
      { "field": "Dimension", "value": "3/8\"" },
      { "field": "Pitch",     "value": "0.75\"" }
    ],

    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP001", "desc": "Fin Press - 1", "preferred": True }
        ]
      }
    ],

    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          { "id": "SM001", "desc": "Shearing M/C 7T", "preferred": True },
          { "id": "SM002", "desc": "Durma shearing M/C", "preferred": True }
        ]
      }
    ],

    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          { "id": "CNCMC002", "desc": "CNC Punching Machine-2", "preferred": True },
          { "id": "CNCMC003", "desc": "CNC Punching Machine-3", "preferred": False }
        ]
      }
    ],

    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          { "id": "BB001",      "desc": "Bending press brake 80T", "preferred": True },
          { "id": "YSDCNC001", "desc": "YSD CNC Press brake",     "preferred": False }
        ]
      }
    ],

    "Hairpin bend": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          { "id": "VBHB003", "desc": "Hairpin bender-3", "preferred": True }
        ]
      }
    ],

    "Expansion": [
      {
        "sequence": 6,
        "conditions": [
          "qty >= 10",
          "FL < 1500",
          "FH < 1219.2",
          "Rows <= 2",
          "L2-L1 <= 50"
        ],
        "machines": [
          { "id": "VEMC001", "desc": "Vertical expander machine", "preferred": True }
        ]
      },
      {
        "sequence": 6,
        "conditions": [
          "Min. qty >= 10 nos.",
          "FL < 2500 mm",
          "FH < 1219.2",
          "Rows <= 3",
          "L1 = L2 = L3"
        ],
        "machines": [
          { "id": "VEMC002", "desc": "Vertical expander machine", "preferred": True }
        ]
      },
      {
        "sequence": 6,
        "conditions": [],
        "machines": [
          { "id": "FB003", "desc": "Flexpander with     balancer -3", "preferred": True },
          { "id": "FB005", "desc": "Flexpander with     balancer -5", "preferred": True },
          
        ]
      }
    ],

    "Coil Bending": [
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          { "id": "CBMC002", "desc": "Coil bending machine", "preferred": True }
        ]
      }
    ],

    "Trimming & Flaring": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          { "id": "TF001", "desc": "Trimming Flaring - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Loading": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          { "id": "RBL001", "desc": "Return Bend Loading - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Brazing": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          { "id": "RBB001", "desc": "Return Bend Brazing - Manual", "preferred": True }
        ]
      }
    ],

    "Header Cutting": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          { "id": "PC001", "desc": "Pipe Cutting", "preferred": True }
        ]
      }
    ],

    "Header Bending": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          { "id": "TBMC001", "desc": "YLM Tube Bending M/C", "preferred": False }
        ]
      }
    ],

    "Header Drilling": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          { "id": "HBDMC001", "desc": "SKB Header brazing / Drilling M/C", "preferred": True },
          { "id": "CNCDMC001","desc": "SKB 4 Axis CNC drilling machine","preferred": True }
        ]
      }
    ],

    "Header End Closing": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          { "id": "TESMC001","desc": "Tube end closing Machine", "preferred": True },
          { "id": "TESMC002","desc": "Tube end closing Machine", "preferred": True }
        ]
      }
    ],

    "Header Branching": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          { "id": "TD001","desc": "T-Forming M/C - HFT-2000","preferred": True }
        ]
      }
    ],

    "Header Hole Piercing": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          { "id": "H001","desc": "Header hole piercing & Extrusion","preferred": False }
        ]
      }
    ],

    "Feeder Cut": [
      {
        "sequence": 17,
        "conditions": [],
        "machines": [
          { "id": "T002","desc": "JDM cut to length m/c","preferred": True }
        ]
      }
    ],

    "Header Sub Assembly": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          { "id": "Manual001","desc": "Brazing - Manual","preferred": True }
        ]
      }
    ],

    "Header to Coil": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          { "id": "Manual002","desc": "Brazing - Manual","preferred": True }
        ]
      }
    ],

    "Leak Testing": [
      {
        "sequence": 20,
        "conditions": [],
        "machines": [
          { "id": "Tank1","desc": "Leak Testing tank - 1","preferred": True },
          { "id": "Tank2","desc": "Leak Testing tank - 2","preferred": False }
        ]
      }
    ],

    "Coil Degreasing": [
      {
        "sequence": 21,
        "conditions": [],
        "machines": [
          { "id": "DegreasingCS1","desc": "Karcher Cleaning Machine 2","preferred": True },
          { "id": "DegreasingCS2","desc": "Karcher Cleaning Machine 3","preferred": True }
        ]
      }
    ],

    "Coating": [
      {
        "sequence": 22,
        "conditions": [],
        "machines": [
          { "id": "Booth1","desc": "Coating booth - 1","preferred": True },
          { "id": "Booth2","desc": "Coating booth - 2","preferred": True },
          { "id": "Booth3","desc": "Coating booth - 3","preferred": True }
        ]
      }
    ]
  }
},

{
  "Cond.S": {
    "header": [
      { "field": "RecipeID",   "value": "R1" },
      { "field": "Dimension",  "value": "3/8\"" },
      { "field": "Pitch",      "value": "0.75\"" },
      { "field": "Qty",         "value": ">=8"}
    ],

    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          {
            "id": "FP001",
            "desc": "Fin Press - 1",
            "preferred": True
          }
        ]
      }
    ],

    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          {
            "id": "SM001",
            "desc": "Shearing M/C 7T",
            "preferred": True
          },
          {
            "id": "SM002",
            "desc": "Durma shearing M/C",
            "preferred": True
          }
        ]
      }
    ],

    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          {
            "id": "CNCMC002",
            "desc": "CNC Punching Machine-2",
            "preferred": True
          },
          {
            "id": "CNCMC003",
            "desc": "CNC Punching Machine-3",
            "preferred": False
          }
        ]
      }
    ],

    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          {
            "id": "BB001",
            "desc": "Bending press brake 80T",
            "preferred": True
          },
          {
            "id": "YSDCNC001",
            "desc": "YSD CNC Press brake",
            "preferred": False
          }
        ]
      }
    ],

    "Hairpin bend": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          {
            "id": "VBHB003",
            "desc": "Hairpin bender-3",
            "preferred": True
          }
        ]
      }
    ],

    "Expansion": [
      {
        "sequence": 6,
        "conditions": [
          { "field": "FH",    "op": "<=", "value": 1219.2 },
          { "field": "FL",    "op": "<=", "value": 2500 },
          { "field": "Rows",  "op": "<=", "value": 4 },
          { "field": "Qty",   "op": ">=", "value": 8 }
        ],
        "machines": [
          {
            "id": "VEMC002",
            "desc": "Vertical expander machine",
            "preferred": True
          }
        ]
      },
      {
        "sequence": 6,
        "conditions": [],
        "machines": [
          {
            "id": "FB003",
            "desc": "Flexpander with     balancer -3",
            "preferred": True
          },
          {
            "id": "FB005",
            "desc": "Flexpander with     balancer -5",
            "preferred": True
          }
        ]
      }
    ],

    "Trimming & Flaring": [
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          {
            "id": "TF001",
            "desc": "Trimming Flaring - Manual",
            "preferred": True
          }
        ]
      }
    ],

    "Return Bend Loading": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          {
            "id": "RBL001",
            "desc": "Return Bend Loading - Manual",
            "preferred": True
          }
        ]
      }
    ],

    "Return Bend Brazing": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          {
            "id": "RBB001",
            "desc": "Return Bend Brazing - Manual",
            "preferred": True
          }
        ]
      }
    ],

    "Header Cutting": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          {
            "id": "PC001",
            "desc": "Pipe Cutting",
            "preferred": True
          }
        ]
      }
    ],

    "Header Bending": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          {
            "id": "TBMC001",
            "desc": "YLM Tube Bending M/C",
            "preferred": False
          }
        ]
      }
    ],

    "Header Drilling": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          {
            "id": "HBDMC001",
            "desc": "SKB Header brazing / Drilling M/C",
            "preferred": True
          },
          {
            "id": "CNCDMC001",
            "desc": "SKB 4 Axis CNC drilling machine",
            "preferred": True
          }
        ]
      }
    ],

    "Header End Closing": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          {
            "id": "TESMC001",
            "desc": "Tube end closing Machine",
            "preferred": True
          },
          {
            "id": "TESMC002",
            "desc": "Tube end closing Machine",
            "preferred": True
          }
        ]
      }
    ],

    "Header Branching": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          {
            "id": "TD001",
            "desc": "T-Forming M/C - HFT-2000",
            "preferred": True
          }
        ]
      }
    ],

    "Header Hole Piercing": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          {
            "id": "H001",
            "desc": "Header hole piercing & Extrusion",
            "preferred": False
          }
        ]
      }
    ],

    "Feeder Cut": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          {
            "id": "T002",
            "desc": "JDM cut to length m/c",
            "preferred": True
          }
        ]
      }
    ],

    "Header Sub Assembly": [
      {
        "sequence": 17,
        "conditions": [],
        "machines": [
          {
            "id": "Manual001",
            "desc": "Brazing - Manual",
            "preferred": True
          }
        ]
      }
    ],

    "Header to Coil": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          {
            "id": "Manual002",
            "desc": "Brazing - Manual",
            "preferred": True
          }
        ]
      }
    ],

    "Leak Testing": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          {
            "id": "Tank1",
            "desc": "Leak Testing tank - 1",
            "preferred": True
          },
          {
            "id": "Tank2",
            "desc": "Leak Testing tank - 2",
            "preferred": False
          }
        ]
      }
    ],

    "Coil Degreasing": [
      {
        "sequence": 20,
        "conditions": [],
        "machines": [
          {
            "id": "DegreasingCS1",
            "desc": "Karcher Cleaning Machine 2",
            "preferred": True
          },
          {
            "id": "DegreasingCS2",
            "desc": "Karcher Cleaning Machine 3",
            "preferred": True
          }
        ]
      }
    ],

    "Coating": [
      {
        "sequence": 21,
        "conditions": [],
        "machines": [
          {
            "id": "Booth1",
            "desc": "Coating booth - 1",
            "preferred": True
          },
          {
            "id": "Booth2",
            "desc": "Coating booth - 2",
            "preferred": True
          },
          {
            "id": "Booth3",
            "desc": "Coating booth - 3",
            "preferred": True
          }
        ]
      }
    ]
  }
},
{
  "FCU": {
    "header": [
      { "field": "RecipeID", "value": "R1"}, 
      { "field": "Dimension", "value": "3/8\"" },
      { "field": "Pitch",    "value": "0.86\"" }
    ],
    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [
          { "field": "Mat", "op": "==", "value": "Cu" }
        ],
        "machines": [
          { "id": "FP001", "preferred": True ,"time-formula" :"(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 150" },
          { "id": "FP002", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 150"
}
        ]
      },
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP001", "preferred": True , "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"},
          { "id": "FP002", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"},
          { "id": "FP006", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"},
          { "id": "FP008", "preferred": True ,"time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170"}
        ]
      }
    ],
    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          { "id": "SM001", "desc": "Shearing M/C 7T",    "preferred": True , "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
          { "id": "SM002", "desc": "Durma Shearing M/C", "preferred": True  , "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
        ]
      }
    ],
    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          { "id": "CNCMC002", "desc": "CNC Punching Machine-2", "preferred": True  , "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
          { "id": "CNCMC003", "desc": "CNC Punching Machine-3", "preferred": False  , "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
        ]
      }
    ],
    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          { "id": "BB001",      "desc": "Bending Press Brake 80T", "preferred": True  , "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
          { "id": "YSDCNC001", "desc": "YSD CNC Press Brake",       "preferred": False  , "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170" },
        ]
      }
    ],
    "Hairpin bend": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          { "id": "VBHB001", "desc": "Hairpin Bender-1", "preferred": True  ,"time-formula": "((((FL + 100)/1000) * (FH/25.4/2) * Row * Qty) / 4) * 50 / 60"},
          { "id": "VBHB003", "desc": "Hairpin Bender-3", "preferred": True ,"time-formula": "((((FL + 100)/1000) * (FH/25.4/2) * Row * Qty) / 4) * 50 / 60"}
        ]
      }
    ],
    "Cut to length": [
      {
        "sequence": 6,
        "conditions": [],
        "machines": [
          { "id": "T001", "desc": "Tridan Cut-to-Length M/C", "preferred": True,"time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60" }
        ]
      }
    ],
    "Expansion": [
      {
        "sequence": 7,
        "conditions": [
          { "field": "FH",   "op": "<",  "value": 1500   },
          { "field": "FL",   "op": "<",  "value": 1219.2 },
          { "field": "Rows", "op": "<=", "value": 4      }
        ],
        "machines": [
          { "id": "VEMC001", "desc": "Vertical Expander Machine", "preferred": True,"time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 72" }
        ]
      },
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          { "id": "VEMC001", "desc": "Vertical Expander Machine", "preferred": True ,"time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 72" },
          { "id": "VEMC002", "desc": "Vertical Expander Machine", "preferred": True ,"time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 72" }

        ]
      }
    ],
    "Trimming Flaring - Manual": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          { "id": "TF001", "desc": "Trimming Flaring – Manual", "preferred": True ,"time-formula": "(FH/25.4) * Row * Qty * 0.33"}
        ]
      }
    ],
    "Return Bend Loading - Manual": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          { "id": "RBL001", "desc": "Return Bend Loading – Manual", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2"}
        ]
      }
    ],
    "Brazing": [
      {
        "sequence": 10,
        "conditions": [
          { "field": "Qty",  "op": ">", "value": 100 },
          { "field": "Rows", "op": "<", "value": 4   }
        ],
        "machines": [
          { "id": "AWMC001", "desc": "Automatic Brazing Oven M/C — HJA-060702", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2"}
        ]
      },
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          { "id": "RBB001", "desc": "Return Bend Brazing – Manual", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" }
        ]
      }
    ],
    "Header Cutting": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          { "id": "PC001", "desc": "Pipe Cutting", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2"}
        ]
      }
    ],
    "Header Bending": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          { "id": "TBMC001", "desc": "YLM Tube Bending M/C", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" }
        ]
      }
    ],
    "Header Drilling": [
      {
        "sequence": 13,
        "conditions": [],
        "machines": [
          { "id": "HBDMC001", "desc": "SKB Header Brazing/Drilling M/C", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" },
          { "id": "CNCDMC001", "desc": "SKB 4-Axis CNC Drilling Machine",  "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" }
        ]
      }
    ],
    "Header End Closing": [
      {
        "sequence": 14,
        "conditions": [],
        "machines": [
          { "id": "TESMC001", "desc": "Tube End Closing Machine", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" },
          { "id": "TESMC002", "desc": "Tube End Closing Machine", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" }
        ]
      }
    ],
    "Header Branching": [
      {
        "sequence": 15,
        "conditions": [],
        "machines": [
          { "id": "TD001", "desc": "T-Forming M/C — HFT-2000", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" }
        ]
      }
    ],
    "Header Hole Piercing": [
      {
        "sequence": 16,
        "conditions": [],
        "machines": [
          { "id": "H001", "desc": "Header Hole Piercing & Extrusion", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" },
        ]
      }
    ],
    "Feeder Cut":[
              {
        "sequence": 17,
        "conditions": [],
        "machines": [
          { "id": "T002", "desc": "JDM Cut-to-Length M/C",           "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" }
        ]
      }
    ],
    "Header Sub Assembly": [
      {
        "sequence": 18,
        "conditions": [],
        "machines": [
          { "id": "Manual001", "desc": "Brazing – Manual", "preferred": True }
        ]
      }
    ],
    "Header to Coil": [
      {
        "sequence": 19,
        "conditions": [],
        "machines": [
          { "id": "Manual002", "desc": "Brazing – Manual", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" }
        ]
      }
    ],
    "Leak Testing": [
      {
        "sequence": 20,
        "conditions": [],
        "machines": [
          { "id": "Tank-FCU", "desc": "Leak Testing Tank-FCU", "preferred": True,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" },
        ]
      }
    ],
    "Coil Degreasing": [
      {
        "sequence": 21,
        "conditions": [],
        "machines": [
          { "id": "DegreasingCS1", "desc": "Karcher Cleaning Machine 2", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" },
          { "id": "DegreasingCS2", "desc": "Karcher Cleaning Machine 3", "preferred": True ,"time-formula": "(FH/25.4/2) * Row * Qty * 0.2" },
        ]
      }
    ],
    "Coating": [
      {
        "sequence": 22,
        "conditions": [],
        "machines": [
          { "id": "Booth1", "desc": "Coating Booth - 1", "preferred": True ,"time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18"},
          { "id": "Booth2", "desc": "Coating Booth - 2", "preferred": True ,"time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18"},
          { "id": "Booth3", "desc": "Coating Booth - 3", "preferred": True,"time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18"},
        ]
      }
    ]
  }
}
,
{
  "Heatpipe": {
    "header": [
      { "field": "RecipeID", "value": "R1" },
      { "field": "Dimension", "value": "1/2\"" },
      { "field": "Pitch",     "value": "1/2" }
    ],

    "Finning / Fin Punching": [
      {
        "sequence": 1,
        "conditions": [
          { "field": "Mat", "op": "==", "value": "Cu" }
        ],
        "machines": [
          { "id": "FP001", "preferred": True },
          { "id": "FP002", "preferred": True }
        ]
      },
      {
        "sequence": 1,
        "conditions": [],
        "machines": [
          { "id": "FP001", "preferred": True },
          { "id": "FP002", "preferred": True },
          { "id": "FP005", "preferred": True },
          { "id": "FP007", "preferred": True }
        ]
      }
    ],

    "Shearing": [
      {
        "sequence": 2,
        "conditions": [],
        "machines": [
          { "id": "SM001", "desc": "Shearing M/C 7T", "preferred": True },
          { "id": "SM002", "desc": "Durma shearing M/C", "preferred": True }
        ]
      }
    ],

    "Punching": [
      {
        "sequence": 3,
        "conditions": [],
        "machines": [
          { "id": "CNCMC002", "desc": "CNC Punching Machine-2", "preferred": False },
          { "id": "CNCMC003", "desc": "CNC Punching Machine-3", "preferred": True }
        ]
      }
    ],

    "Bending": [
      {
        "sequence": 4,
        "conditions": [],
        "machines": [
          { "id": "BB001", "desc": "Bending press brake 80T", "preferred": True },
          { "id": "YSDCNC001", "desc": "YSD CNC Press brake", "preferred": True }
        ]
      }
    ],

    "Hairpin bend": [
      {
        "sequence": 5,
        "conditions": [],
        "machines": [
          { "id": "VBHB002", "desc": "Hairpin bender-2", "preferred": True }
        ]
      }
    ],

    "Cut to length": [
      {
        "sequence": 6,
        "conditions": [
          { "field": "FL", "op": ">", "value": 2800 }
        ],
        "machines": [
          { "id": "T001", "desc": "Tridan cut to length m/c.", "preferred": True },
          
        ]
      },
      {
        "sequence": 6,
        "conditions": [],
        "machines": [
          { "id": "T002", "desc": "BP cut to length m/c.", "preferred": True }
        ]
      }
    ],

    "Expansion": [
      {
        "sequence": 7,
        "conditions": [],
        "machines": [
          { "id": "FB006", "desc": "Flexpander with     balancer -6", "preferred": True }
        ]
      }
    ],

    "Trimming & Flaring": [
      {
        "sequence": 8,
        "conditions": [],
        "machines": [
          { "id": "TF001", "desc": "Trimming Flaring - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Loading": [
      {
        "sequence": 9,
        "conditions": [],
        "machines": [
          { "id": "RBL001", "desc": "Return Bend Loading - Manual", "preferred": True }
        ]
      }
    ],

    "Return Bend Brazing": [
      {
        "sequence": 10,
        "conditions": [],
        "machines": [
          { "id": "RBB001", "desc": "Return Bend Brazing - Manual", "preferred": True }
        ]
      }
    ],

    "Coil Degreasing": [
      {
        "sequence": 11,
        "conditions": [],
        "machines": [
          { "id": "DegreasingCS1", "desc": "Karcher Cleaning Machine 2", "preferred": True },
          { "id": "DegreasingCS2", "desc": "Karcher Cleaning Machine 3", "preferred": True }
        ]
      }
    ],

    "Coating": [
      {
        "sequence": 12,
        "conditions": [],
        "machines": [
          { "id": "Booth1", "desc": "Coating booth - 1", "preferred": True },
          { "id": "Booth2", "desc": "Coating booth - 2", "preferred": True },
          { "id": "Booth3", "desc": "Coating booth - 3", "preferred": True }
        ]
      }
    ]
  }
}

]


MACHINE_TIME_FORMULA = [
  {
    "machine": "FP001",
    "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 150",
          "value": 62
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 150"
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 52
        },
        "1.5\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 35
        }
      }
    }
  },
  {
    "machine": "FP002",
    "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 150",
          "value": 62
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 150"
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 52
        },
        "1.5\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 35
        }
      }
    }
  },
  {
    "machine": "FP003",
    "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 150",
          "value": 62
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 150"
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 52
        },
        "1.5\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 35
        }
      }
    }
  },
  {
    "machine": "FP005",
    "formulas": {
      "3/8\"": {
        "0.86\"": { "time-formula": None },
        "0.75\"": { "time-formula": None }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 170"
        }
      },
      "5/8\"": {
        "P40": { "time-formula": None },
        "1.5\"": { "time-formula": None },
        "60x30": { "time-formula": None }
      }
    }
  },
  {
    "machine": "FP006",
    "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 66
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": None
        },
        "1.5\"": {
          "time-formula": None
        },
        "60x30": {
          "time-formula": None
        }
      }
    }
  },
  {
    "machine": "FP007",
    "formulas": {
      "3/8\"": {
        "0.86\"": { "time-formula": None },
        "0.75\"": { "time-formula": None }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 66
        }
      },
      "5/8\"": {
        "P40": { "time-formula": None },
        "1.5\"": { "time-formula": None },
        "60x30": { "time-formula": None }
      }
    }
  },
  {
    "machine": "FP008",
    "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "0.75\"": { "time-formula": None }
      },
      "1/2\"": {
        "1/2": { "time-formula": None }
      },
      "5/8\"": {
        "P40": { "time-formula": None },
        "1.5\"": { "time-formula": None },
        "60x30": { "time-formula": None }
      }
    }
  },
  {
    "machine": "SM001",
    "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 66
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 52
        },
        "1.5\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 35
        }
      }
    }
  },
  {
    "machine": "SM002",
      "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 66
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 52
        },
        "1.5\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 35
        }
      }
    }
  },
  {
    "machine": "CNCMC002",
      "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
          "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 66
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 52
        },
        "1.5\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 35
        }
      }
    }
  },
  {
    "machine": "CNCMC003",
      "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
        "1/2":{
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 66
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 52
        },
        "1.5\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 35
        }
      }
    }
  },
  {
    "machine": "BB001",
      "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
         "1/2": {
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 66
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 52
        },
        "1.5\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 35
        }
      }
    }
  },
  {
    "machine": "YSDCNC001",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        }
      },
      "1/2\"": {
           "1/2":{
          "time-formula": "(FH/31.75) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 66
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 52
        },
        "1.5\"": {
          "time-formula": "(FH/25.4) * Row * (FL/25.4) * FPI * Qty / 12 / 170",
          "value": 55
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * (FL/25.4) * FPI * Qty / 8 / 170",
          "value": 35
        }
      }
    }
  },
    {
    "machine": "VBHB001",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "((((FL + 100)/1000) * (FH/25.4/2) * Row * Qty) / 4) * 50 / 60",
          "value": 18
        },
        "0.75\"": {
          "time-formula": "",
          "value": ""
        }
      },
      "1/2\"": {
         "1/2":{
          "time-formula": "",
          "value": ""
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
  },
    {
    "machine": "VBHB002",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "((((FL + 100)/1000) * (FH/25.4/2) * Row * Qty) / 4) * 50 / 60",
          "value": 18
        },
        "0.75\"": {
          "time-formula": "((((FL + 100)/1000) * (FH/25.4/2) * Row * Qty) / 4) * 50 / 60",
          "value": 18
        }
      },
      "1/2\"": {
       "1/2":{
          "time-formula": "",
          "value": ""
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
  },
  {
    "machine": "VBHB003",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "((((FL + 100)/1000) * (FH/25.4/2) * Row * Qty) / 4) * 50 / 60",
          "value": 18
        },
        "0.75\"": {
          "time-formula": "((((FL + 100)/1000) * (FH/25.4/2) * Row * Qty) / 4) * 50 / 60",
          "value": 18
        }
      },
      "1/2\"": {
        "1/2":{
          "time-formula": "",
          "value": ""
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
  },
  {
    "machine": "T001",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60",
          "value": 103
        },
        "0.75\"": {
          "time-formula": "",
          "value": ""
        }
      },
      "1/2\"": {
        "1/2":{
          "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60",
          "value": 103
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60",
          "value": 103
        },
        "1.5\"": {
          "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60",
          "value": 103
        },
        "60x30": {
          "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60",
          "value": 103
        }
      }
    }
  },
  {
    "machine": "T002",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "",
          "value": ""
        },
        "0.75\"": {
          "time-formula": "",
          "value": ""
        }
      },
      "1/2\"": {
        "1/2":{
          "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60",
          "value": 103
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60",
          "value": 103
        },
        "1.5\"": {
          "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60",
          "value": 103
        },
        "60x30": {
          "time-formula": "(((FL + 100)/1000) * (FH/25.4) * Row * Qty) * 35 / 60",
          "value": 103
        }
      }
    }
  },
     {
    "machine": "VEMC001",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 72",
          "value": 0.63
        },
        "0.75\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 72",
          "value": 0.63
        }
      },
      "1/2\"": {
      "1/2": {
          "time-formula": "",
          "value": ""
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
  },
  {
    "machine": "VEMC002",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 72",
          "value": 0.63
        },
        "0.75\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 72",
          "value": 0.63
        }
      },
      "1/2\"": {
         "1/2": {
          "time-formula": "",
          "value": ""
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
},
   {
    "machine": "FB003",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 50",
          "value": 0.91
        },
        "0.75\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 50",
          "value": 0.91
        }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "",
          "value": ""
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
  },
  {
    "machine": "FB004",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "",
          "value": ""
        },
        "0.75\"": {
          "time-formula": "",
          "value": ""
        }
      },
      "1/2\"": {
         "1/2": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 50",
          "value": 0.91
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
  },
    {
    "machine": "FB005",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 50",
          "value": 0.91
        },
        "0.75\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 50",
          "value": 0.91
        }
      },
      "1/2\"": {
        "1/2": {
          "time-formula": "",
          "value": ""
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
  },
      {
    "machine": "FB006",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "",
          "value": ""
        },
        "0.75\"": {
          "time-formula": "",
          "value": ""
        }
      },
      "1/2\"": {
          "1/2":{
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 50",
          "value": 0.91
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
  }
 ,
 {
    "machine": "HB001",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "",
          "value": ""
        },
        "0.75\"": {
          "time-formula": "",
          "value": ""
        }
      },
      "1/2\"": {
           "1/2":{
          "time-formula": "",
          "value": ""
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 55",
          "value": 0.83
        },
        "1.5\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 55",
          "value": 0.83
        },
        "60x30": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Row * Qty / 144 / 55",
          "value": 0.83
        }
      }
    }
  },
   {
    "machine": "CBMC002",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "",
          "value": ""
        },
        "0.75\"": {
          "time-formula": "",
          "value": ""
        }
      },
      "1/2\"": {
         "1/2": {
          "time-formula": "",
          "value": ""
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "",
          "value": ""
        },
        "1.5\"": {
          "time-formula": "",
          "value": ""
        },
        "60x30": {
          "time-formula": "",
          "value": ""
        }
      }
    }
  },
     {
    "machine": "TF001",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4) * Row * Qty * 0.33 ",
          "value": 29.04
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * Qty * 0.33 ",
          "value": 29.04
        }
      },
      "1/2\"": {
         "1/2": {
          "time-formula": "(FH/31.75) * Row * Qty * 0.33 ",
          "value": 23.23
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * Qty * 0.33 * 2",
          "value": 36.88
        },
        "1.5\"": {
          "time-formula": "(FH/38.1) * Row * Qty * 0.33 * 2 ",
          "value": 38.72
        },
        "60x30": {
          "time-formula": "(FH/38.1) * Row * Qty * 0.33 * 2 ",
          "value": 24.59
        }
      }
    }
  },
   {
    "machine": "RBL001",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FH/25.4/2) * Row * Qty * 0.2",
          "value": 8.80
        },
        "0.75\"": {
          "time-formula": "(FH/25.4) * Row * Qty * 0.2  ",
          "value": 17.60
        }
      },
      "1/2\"": {
         "1/2": {
          "time-formula": "(FH/31.75) * Row * Qty * 0.2 ",
          "value": 14.08
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FH/40) * Row * Qty * 0.2 * 2 ",
          "value": 22.35
        },
        "1.5\"": {
          "time-formula": "(FH/38.1) * Row * Qty * 0.2 * 2 ",
          "value": 23.47
        },
        "60x30": {
          "time-formula": "(FH/60) * Row * Qty * 0.2 * 2",
          "value": 14.90
        }
      }
    }
  },
  {
    "machine": "Booth1",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        },
        "0.75\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        }
      },
      "1/2\"": {
          "1/2":{
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        },
        "1.5\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        },
        "60x30": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        }
      }
    }
  },
  {
    "machine": "Booth2",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        },
        "0.75\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        }
      },
      "1/2\"": {
         "1/2": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        },
        "1.5\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        },
        "60x30": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        }
      }
    }
  },
  {
    "machine": "Booth3",
       "formulas": {
      "3/8\"": {
        "0.86\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        },
        "0.75\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        }
      },
      "1/2\"": {
         "1/2": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        }
      },
      "5/8\"": {
        "P40": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        },
        "1.5\"": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        },
        "60x30": {
          "time-formula": "(FL/25.4) * (FH/25.4) * Qty / 144 / 18 ",
          "value": 1.27
        }
      }
    }
  }
   

]