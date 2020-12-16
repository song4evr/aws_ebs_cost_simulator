

class ssd_volume():
    def __init__(self, volume_size, **kwargs):

        self.init_volume_size(volume_size=volume_size, **kwargs)
        self.get_IOPS(**kwargs)
        self.get_throughput(**kwargs)
        self.get_cost(**kwargs)
        
    def init_volume_size(self, volume_size, **kwargs):
        
        if self.min_size >= volume_size:
            self.volume_size = self.min_size
        elif self.max_size <= volume_size:
            self.volume_size = self.max_size
        else: 
            self.volume_size = volume_size

class gp3(ssd_volume):
    price_per_GB = 0.08
    price_per_IOPS = 0.005
    price_per_throughput = 0.04


    # 1 GiB
    min_size = 1
    # 16 TiB == 16384 GiB
    max_size = 16 * 1024

    min_IOPS = 3000

    def __init__(self, volume_size, IOPS, throughput, **kwargs):
        super().__init__(volume_size=volume_size, IOPS=IOPS, throughput=throughput, **kwargs)

    def get_IOPS(self, IOPS, **kwargs):
        max_IOPS_per_volume_GiB_ratio = 500 # 500 IOPS per GiB
        max_IOPS = self.volume_size * max_IOPS_per_volume_GiB_ratio

        max_IOPS = max_IOPS if max_IOPS < 16000 else 16000
        if max_IOPS < self.min_IOPS:
            max_IOPS = self.min_IOPS
        if IOPS <= self.min_IOPS:
            self.IOPS = self.min_IOPS
        elif IOPS < max_IOPS:
            self.IOPS = IOPS
        else:
            self.IOPS = max_IOPS

    def get_throughput(self, throughput, **kwargs):
        max_throughput_per_IOPS_ratio = 0.25 # 0.25 MiB/s per IOPS
        min_throughput = 125
        

        max_throughput = self.IOPS * max_throughput_per_IOPS_ratio
        max_throughput = max_throughput if max_throughput < 1000 else 1000
        if throughput <= min_throughput:
            self.throughput = min_throughput
        elif throughput >= max_throughput:
            self.throughput = max_throughput
        else:
            self.throughput = throughput

    def get_cost(self, **kwargs):
        cost_by_size = self.volume_size * self.price_per_GB 
        cost_by_IOPS =  0
        if self.IOPS > 3000:
            cost_by_IOPS = self.price_per_IOPS * (self.IOPS-3000)
        cost_by_throughput = 0
        if self.throughput > 125:
            cost_by_throughput = self.price_per_throughput * (self.throughput-125)
        self.cost_per_month = cost_by_size + cost_by_IOPS + cost_by_throughput


class gp2(ssd_volume):

    ## 3 IOPS per GiB
    IO_GiB_ratio = 3

    # 1 GiB
    min_size = 1
    # 16 TiB == 16384 GiB
    max_size = 16 * 1024

    min_IOPS = 3000 #burst
    max_IOPS = 16000
    # max throughput 1,000 MB/s
    max_throughput = 1000

    price_per_GB = 0.10

    def __init__(self,volume_size, **kwargs):

        #self.volume_size = volume_size
        super().__init__(volume_size=volume_size, **kwargs)
        
    def get_IOPS(self, **kwargs):
        IOPS = self.volume_size * self.IO_GiB_ratio

        if IOPS <= self.min_IOPS:
            self.IOPS = self.min_IOPS
        elif IOPS < self.max_IOPS:
            self.IOPS = IOPS
        else:
            self.IOPS = self.max_IOPS

    def get_throughput(self, **kwargs):
        if self.volume_size <= 170:
            self.throughput = 128
        elif self.volume_size < 334:
            self.throughput = 250
        else:
            self.throughput = 250

    def get_cost(self, **kwargs):
        self.cost_per_month = self.volume_size * self.price_per_GB




if __name__ == '__main__':

    gp2_min = gp2(1)

    assert gp2_min.volume_size == 1
    assert gp2_min.throughput == 128
    assert gp2_min.IOPS == 3000


    gp2_max = gp2(20000)

    assert gp2_max.volume_size == 16*1024
    assert gp2_max.throughput == 250
    assert gp2_max.IOPS == 16000


    gp3_min = gp3(1,1,1)

    gp3_min = gp3(1,1,1)

    assert gp3_min.volume_size == 1
    assert gp3_min.throughput == 125
    assert gp3_min.IOPS == 3000


    gp3_max = gp3(200000,200000,200000)

    assert gp3_max.volume_size == 16*1024
    assert gp3_max.throughput == 1000
    assert gp3_max.IOPS == 16000