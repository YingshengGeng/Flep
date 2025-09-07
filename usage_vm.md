# 编译
sudo /home/gys/bf-sde-9.13.2/install/bin/bf-p4c --std p4-16 --target tofino --arch tna  -o /home/gys/xian/xian_test/flep_encap_with_topo/target/ -g /home/gys/xian/xian_test/flep_encap_with_topo/flep_encap.p4

sudo cp /home/gys/xian/xian_test/flep_encap_with_topo/target/flep_encap.conf /home/gys/bf-sde-9.13.2/install/share/p4/targets/tofino/


sudo /home/gys/bf-sde-9.13.2/install/bin/bf-p4c --std p4-16 --target tofino --arch tna  -o /home/gys/xian/xian_test/flep_process_with_topo/target/ -g /home/gys/xian/xian_test/flep_process_with_topo/flep_process.p4

sudo cp /home/gys/xian/xian_test/flep_process_with_topo/target/flep_process.conf /home/gys/bf-sde-9.13.2/install/share/p4/targets/tofino/


# 运行
cd $SDE
./run_tofino_model.sh -p 程序名称
./run_switchd.sh -p 程序名称
./run_bfshell.sh -b 程序名称




# 其他 
注意两者的程序运行方式不同
- 硬件上
p = Popen(
    "bash $SDE_INSTALL/bin/run_bfshell.sh -b " + CONFIG_PATH,
    shell=True,
    stdout=PIPE,
    stderr=PIPE,
    env={"SDE": parameter["SDE"], "SDE_INSTALL": parameter["SDE_INSTALL"]},
)

- 软件上
p = Popen(
    "bash $SDE/run_bfshell.sh -b " + CONFIG_PATH,
    shell=True,
    stdout=PIPE,
    stderr=PIPE,
    env={"SDE": parameter["SDE"], "SDE_INSTALL": parameter["SDE_INSTALL"]},
)




```
# start network
sudo python network.py $SDE

# controller code
mx s1 
$SDE/run_bfshell.sh -b `pwd`/controller_1.py

# controller code
mx s2
$SDE/run_bfshell.sh -b `pwd`/controller_2.py

# start receiver
mx h2
python receive.py

# send 1500 packets, and observe how only 1000 are received
mx h1 
python send.py 10.2.2.2 1500
```


DE_INSTALL : "/home/gys/bf-sde-9.13.2/install"
SDE : "/home/gys/bf-sde-9.13.2"
PYTHON_VERSION: "python3.10"